# methods/model_modifications.py

from .base_method import BaseMethod
import torch
import copy

class ModelModification(BaseMethod):
    def __init__(self):
        super().__init__()

    def apply(self, model):
        """
        Modify the model to prevent forbidden content generation.
        """
        return model

# https://github.com/rohitgandikota/unified-concept-editing - modified and refactored to work with SDXL
class ConceptEditing(ModelModification):
    def __init__(self, old_text_=None, new_text_=None, retain_text_=None, 
                 lamb=1, erase_scale=0.1, preserve_scale=0.1, technique='tensor'):
        super().__init__()
        self.old_text_ = old_text_
        self.new_text_ = new_text_
        self.retain_text_ = retain_text_
        self.lamb = lamb
        self.erase_scale = erase_scale
        self.preserve_scale = preserve_scale
        self.technique = technique

    def apply(self, ldm_stable, train_from_scratch=False):
        """
        Apply concept editing to the model
        """
        if train_from_scratch is False:
            # TODO add model path (huggingface probably)
            ldm_stable.unet.load_state_dict(
                torch.load(f'models/{model_name}', map_location=device)
            )
            return ldm_stable
        # Get cross-attention layers
        ca_layers = []
        sub_nets = ldm_stable.unet.named_children()
        for net in sub_nets:
            if 'up' in net[0] or 'down' in net[0]:
                for block in net[1]:
                    if 'Cross' in block.__class__.__name__:
                        for attn in block.attentions:
                            for transformer in attn.transformer_blocks:
                                ca_layers.append(transformer.attn2)
            if 'mid' in net[0]:
                for attn in net[1].attentions:
                    for transformer in attn.transformer_blocks:
                        ca_layers.append(transformer.attn2)

        # Initialize projection matrices
        projection_matrices = []
        og_matrices = []

        # Get to_v and to_k matrices
        for l in ca_layers:
            projection_matrices.append(l.to_v)
            og_matrices.append(copy.deepcopy(l.to_v))
            projection_matrices.append(l.to_k)
            og_matrices.append(copy.deepcopy(l.to_k))

        # Reset parameters
        num_layers = len(ca_layers)
        for idx in range(num_layers):
            ca_layers[idx].to_v = copy.deepcopy(og_matrices[idx*2])
            ca_layers[idx].to_k = copy.deepcopy(og_matrices[idx*2+1])
            projection_matrices[idx*2] = ca_layers[idx].to_v
            projection_matrices[idx*2+1] = ca_layers[idx].to_k

        # Process text inputs
        old_texts = [self.old_text_] if isinstance(self.old_text_, str) else self.old_text_
        new_texts = [t if t != '' else ' ' for t in self.new_text_]
        ret_texts = self.retain_text_ if self.retain_text_ is not None else ['']
        retain = self.retain_text_ is not None

        # Edit each projection matrix
        for layer_num, proj_matrix in enumerate(projection_matrices):
            with torch.no_grad():
                # Initialize matrices
                hidden_dim = proj_matrix.weight.shape[0]
                embed_dim = proj_matrix.weight.shape[1]
                mat1 = self.lamb * proj_matrix.weight
                mat2 = self.lamb * torch.eye(embed_dim, device=proj_matrix.weight.device)
                mat1 = mat1.float()
                mat2 = mat2.float()

                # Process each text pair
                for old_text, new_text in zip(old_texts, new_texts):
                    # Get embeddings from both encoders
                    text_input = ldm_stable.tokenizer_2(
                        [old_text, new_text],
                        padding="max_length",
                        max_length=ldm_stable.tokenizer_2.model_max_length,
                        truncation=True,
                        return_tensors="pt",
                    ).to(ldm_stable.device)

                    text_input1 = ldm_stable.tokenizer(
                        [old_text, new_text],
                        padding="max_length",
                        max_length=ldm_stable.tokenizer.model_max_length,
                        truncation=True,
                        return_tensors="pt",
                    ).to(ldm_stable.device)

                    embeddings1 = ldm_stable.text_encoder(
                        text_input1.input_ids,
                        output_hidden_states=True
                    ).hidden_states[-2]  # 768 dim
                    
                    embeddings2 = ldm_stable.text_encoder_2(
                        text_input.input_ids,
                        output_hidden_states=True
                    ).hidden_states[-2]  # 1280 dim
                    
                    embeddings = torch.cat([embeddings1, embeddings2], dim=-1)  # 2048 dim

                    # Process token indices
                    final_token_idx = text_input.attention_mask[0].sum().item()-2
                    final_token_idx_new = text_input.attention_mask[1].sum().item()-2
                    farthest = max([final_token_idx_new, final_token_idx])
                    
                    old_emb = embeddings[0]
                    old_emb = old_emb[final_token_idx:len(old_emb)-max(0,farthest-final_token_idx)]
                    new_emb = embeddings[1]
                    new_emb = new_emb[final_token_idx_new:len(new_emb)-max(0,farthest-final_token_idx_new)]

                    # Project embeddings
                    old_proj = torch.mm(old_emb, proj_matrix.weight.t())
                    new_proj = torch.mm(new_emb, proj_matrix.weight.t())

                    if self.technique == 'tensor':
                        u = old_proj / old_proj.norm(dim=-1, keepdim=True)
                        new_proj_scalar = (u * new_proj).sum()
                        target = new_proj - new_proj_scalar * u
                    else:
                        target = new_proj

                    # Update matrices
                    old_emb_flat = old_emb.view(-1, embed_dim).float()
                    target_flat = target.view(-1, hidden_dim).float()
                    mat1 += self.erase_scale * torch.mm(target_flat.t(), old_emb_flat)
                    mat2 += self.erase_scale * torch.mm(old_emb_flat.t(), old_emb_flat)

                    # Handle preservation if specified
                    if retain:
                        for text in ret_texts:
                            text_input1 = ldm_stable.tokenizer(
                                [text, text],
                                padding="max_length",
                                max_length=ldm_stable.tokenizer.model_max_length,
                                truncation=True,
                                return_tensors="pt",
                            ).to(ldm_stable.device)
                            
                            text_input2 = ldm_stable.tokenizer_2(
                                [text, text],
                                padding="max_length",
                                max_length=ldm_stable.tokenizer_2.model_max_length,
                                truncation=True,
                                return_tensors="pt",
                            ).to(ldm_stable.device)

                            emb1 = ldm_stable.text_encoder(
                                text_input1.input_ids,
                                output_hidden_states=True
                            ).hidden_states[-2]
                            
                            emb2 = ldm_stable.text_encoder_2(
                                text_input2.input_ids,
                                output_hidden_states=True
                            ).hidden_states[-2]
                            
                            emb = torch.cat([emb1, emb2], dim=-1)
                            
                            old_emb, new_emb = emb[0], emb[1]
                            old_proj = torch.mm(old_emb, proj_matrix.weight.t())
                            new_proj = torch.mm(new_emb, proj_matrix.weight.t())
                            target = new_proj

                            old_emb_flat = old_emb.view(-1, embed_dim).float()
                            target_flat = target.view(-1, hidden_dim).float()
                            mat1 += self.preserve_scale * torch.mm(target_flat.t(), old_emb_flat)
                            mat2 += self.preserve_scale * torch.mm(old_emb_flat.t(), old_emb_flat)

                # Update projection matrix
                proj_matrix.weight = torch.nn.Parameter(torch.mm(mat1, torch.inverse(mat2)).bfloat16())

        return ldm_stable