# from transformers import AutoTokenizer, AutoModel
# import torch
# from scipy.spatial.distance import cosine

# # 函数来计算句子向量
# def get_sentence_embedding(sentence, model, tokenizer):
#     # 对句子进行编码，并转换为模型需要的格式
#     encoded_input = tokenizer(sentence, padding=True, truncation=True, return_tensors='pt')
    
#     # 计算句子的向量表示
#     with torch.no_grad():
#         model_output = model(**encoded_input)
    
#     # 取均值作为句子的向量表示
#     sentence_embedding = torch.mean(model_output.last_hidden_state, dim=1).squeeze()
#     return sentence_embedding

# # 函数来比较两个句子的相似度
# def semantic_similarity(sentence1, sentence2, threshold=0.8):

#     # 加载模型和分词器
#     tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/bert-base-nli-mean-tokens')
#     model = AutoModel.from_pretrained('sentence-transformers/bert-base-nli-mean-tokens')
    
#     # 计算句子的向量
#     sentence_embedding1 = get_sentence_embedding(sentence1, model, tokenizer)
#     sentence_embedding2 = get_sentence_embedding(sentence2, model, tokenizer)
    
#     # 计算两个向量之间的余弦相似度
#     similarity = 1 - cosine(sentence_embedding1, sentence_embedding2)
    
#     # 判断相似度是否超过阈值
#     return similarity, similarity > threshold


from sentence_transformers import SentenceTransformer, util
import logging

def compute_sentence_similiarity(sentence1, sentence2):
    """
    计算两个句子的相似度
    """
    # 加载模型
    model = SentenceTransformer('/data/jxq/mobile-agent/comparison_algorithm/all-MiniLM-L6-v2')

    # 计算句子的向量
    sentence_embedding1 = model.encode(sentence1, convert_to_tensor=True)
    sentence_embedding2 = model.encode(sentence2, convert_to_tensor=True)

    # 计算两个向量之间的余弦相似度
    similarity = util.pytorch_cos_sim(sentence_embedding1, sentence_embedding2)[0][0]

    return similarity

def check_sentence_similarity(sentence1, sentence2, threshold=0.8):
    """
    检查两个句子是否相似
    """
    logging.info(f"sentence similarity threshold: {threshold}")
    similarity = compute_sentence_similiarity(sentence1, sentence2)
    return similarity, similarity > threshold

# model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# #Compute embedding for both lists
# embedding_1= model.encode(sentences[0], convert_to_tensor=True)
# embedding_2 = model.encode(sentences[1], convert_to_tensor=True)

# util.pytorch_cos_sim(embedding_1, embedding_2)
## tensor([[0.6003]])


if __name__ == "__main__": 
    # 输入两个句子
    sentence1 = "What's the weather like in Singapore?"
    sentence2 = "weather like in Singapore?"

    # 计算相似度
    similarity, is_similar = check_sentence_similarity(sentence1, sentence2)

    print(f"Similarity: {similarity}")
    print("The sentences are semantically " + ("similar" if is_similar else "not similar"))
