# -*- coding: utf-8 -*-
import re
SRC = 'extracted/Contents/section0.xml'
d = open(SRC, encoding='utf-8').read()

REFS = [
("[1] D. Nadeau and S. Sekine, \"A Survey of Named Entity Recognition and Classification,\" Lingvisticae Investigationes, Vol. 30, No. 1, pp. 3-26, 2007.",
 "[1] D. Nadeau and S. Sekine, \"A Survey of Named Entity Recognition and Classification,\" Lingvisticae Investigationes, Vol. 30, No. 1, pp. 3-26, Jan. 2007. https://doi.org/10.1075/li.30.1.03nad"),

("[2] A. Ritter, S. Clark, Mausam, and O. Etzioni, \"Named Entity Recognition in Tweets: An Experimental Study,\" Proc. of the Conf. on Empirical Methods in Natural Language Processing(EMNLP), pp. 1524-1534, 2011.",
 "[2] A. Ritter, S. Clark, Mausam, and O. Etzioni, \"Named Entity Recognition in Tweets: An Experimental Study,\" Proc. of the Conf. on Empirical Methods in Natural Language Processing(EMNLP), Edinburgh, UK, pp. 1524-1534, Jul. 2011. https://doi.org/10.5555/2145432.2145595"),

("[3] G. Lample, M. Ballesteros, S. Subramanian, K. Kawakami, and C. Dyer, \"Neural Architectures for Named Entity Recognition,\" Proc. of NAACL-HLT, pp. 260-270, 2016.",
 "[3] G. Lample, M. Ballesteros, S. Subramanian, K. Kawakami, and C. Dyer, \"Neural Architectures for Named Entity Recognition,\" Proc. of NAACL-HLT, San Diego, CA, USA, pp. 260-270, Jun. 2016. https://doi.org/10.18653/v1/N16-1030"),

("[4] J. Devlin, M. W. Chang, K. Lee, and K. Toutanova, \"BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding,\" Proc. of NAACL-HLT, pp. 4171-4186, 2019.",
 "[4] J. Devlin, M. W. Chang, K. Lee, and K. Toutanova, \"BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding,\" Proc. of NAACL-HLT, Minneapolis, MN, USA, pp. 4171-4186, Jun. 2019. https://doi.org/10.18653/v1/N19-1423"),

("[5] A. Vaswani et al., \"Attention Is All You Need,\" Advances in Neural Information Processing Systems(NeurIPS), Vol. 30, pp. 5998-6008, 2017.",
 "[5] A. Vaswani et al., \"Attention Is All You Need,\" Advances in Neural Information Processing Systems(NeurIPS), Vol. 30, pp. 5998-6008, Dec. 2017. https://doi.org/10.48550/arXiv.1706.03762"),

("[6] T. B. Brown et al., \"Language Models are Few-Shot Learners,\" Advances in Neural Information Processing Systems(NeurIPS), Vol. 33, pp. 1877-1901, 2020.",
 "[6] T. B. Brown et al., \"Language Models are Few-Shot Learners,\" Advances in Neural Information Processing Systems(NeurIPS), Vol. 33, pp. 1877-1901, Dec. 2020. https://doi.org/10.48550/arXiv.2005.14165"),

("[7] J. Wei et al., \"Emergent Abilities of Large Language Models,\" arXiv preprint arXiv:2206.07682, 2022.",
 "[7] J. Wei et al., \"Emergent Abilities of Large Language Models,\" arXiv preprint arXiv:2206.07682, Jun. 2022. https://doi.org/10.48550/arXiv.2206.07682"),

("[8] L. Ouyang et al., \"Training Language Models to Follow Instructions with Human Feedback,\" Advances in Neural Information Processing Systems(NeurIPS), Vol. 35, pp. 27730-27744, 2022.",
 "[8] L. Ouyang et al., \"Training Language Models to Follow Instructions with Human Feedback,\" Advances in Neural Information Processing Systems(NeurIPS), Vol. 35, pp. 27730-27744, Dec. 2022. https://doi.org/10.48550/arXiv.2203.02155"),

("[9] X. Wei et al., \"Zero-Shot Information Extraction via Chatting with ChatGPT,\" arXiv preprint arXiv:2302.10205, 2023.",
 "[9] X. Wei et al., \"Zero-Shot Information Extraction via Chatting with ChatGPT,\" arXiv preprint arXiv:2302.10205, Feb. 2023. https://doi.org/10.48550/arXiv.2302.10205"),

("[10] J. Achiam et al., \"GPT-4 Technical Report,\" arXiv preprint arXiv:2303.08774, 2023.",
 "[10] J. Achiam et al., \"GPT-4 Technical Report,\" arXiv preprint arXiv:2303.08774, Mar. 2023. https://doi.org/10.48550/arXiv.2303.08774"),

("[11] P. N. Bennett and J. G. Carbonell, \"Detecting Action-Items in E-mail,\" Proc. of the 28th Annual Int. ACM SIGIR Conf. on Research and Development in Information Retrieval, pp. 585-586, 2005.",
 "[11] P. N. Bennett and J. G. Carbonell, \"Detecting Action-Items in E-mail,\" Proc. of the 28th Annual Int. ACM SIGIR Conf. on Research and Development in Information Retrieval, Salvador, Brazil, pp. 585-586, Aug. 2005. https://doi.org/10.1145/1076034.1076140"),

("[12] M. Purver, P. Ehlen, and J. Niekrasz, \"Detecting Action Items in Multi-party Meetings: Annotation and Initial Experiments,\" Machine Learning for Multimodal Interaction(MLMI), LNCS Vol. 4299, pp. 200-211, 2006.",
 "[12] M. Purver, P. Ehlen, and J. Niekrasz, \"Detecting Action Items in Multi-party Meetings: Annotation and Initial Experiments,\" Machine Learning for Multimodal Interaction(MLMI), LNCS Vol. 4299, pp. 200-211, May 2006. https://doi.org/10.1007/11965152_18"),

("[13] T. L. Saaty, The Analytic Hierarchy Process, McGraw-Hill, New York, 1980.",
 "[13] T. L. Saaty, \"How to Make a Decision: The Analytic Hierarchy Process,\" European Journal of Operational Research, Vol. 48, No. 1, pp. 9-26, Sep. 1990. https://doi.org/10.1016/0377-2217(90)90057-I"),

("[14] S. Greco, M. Ehrgott, and J. R. Figueira (eds.), Multiple Criteria Decision Analysis: State of the Art Surveys, Springer, 2nd ed., 2016.",
 "[14] S. Greco, M. Ehrgott, and J. R. Figueira (eds.), Multiple Criteria Decision Analysis: State of the Art Surveys, 2nd ed., Springer, New York, NY, USA, 2016. https://doi.org/10.1007/978-1-4939-3094-4"),

("[15] S. Ghanbari and M. Othman, \"A Priority Based Job Scheduling Algorithm in Cloud Computing,\" Procedia Engineering, Vol. 50, pp. 778-785, 2012.",
 "[15] S. Ghanbari and M. Othman, \"A Priority Based Job Scheduling Algorithm in Cloud Computing,\" Procedia Engineering, Vol. 50, pp. 778-785, Oct. 2012. https://doi.org/10.1016/j.proeng.2012.10.086"),

("[16] M. T. Ribeiro, S. Singh, and C. Guestrin, \"Why Should I Trust You?: Explaining the Predictions of Any Classifier,\" Proc. of the 22nd ACM SIGKDD Int. Conf. on Knowledge Discovery and Data Mining, pp. 1135-1144, 2016.",
 "[16] M. T. Ribeiro, S. Singh, and C. Guestrin, \"Why Should I Trust You?: Explaining the Predictions of Any Classifier,\" Proc. of the 22nd ACM SIGKDD Int. Conf. on Knowledge Discovery and Data Mining, San Francisco, CA, USA, pp. 1135-1144, Aug. 2016. https://doi.org/10.1145/2939672.2939778"),

("[17] S. M. Lundberg and S.-I. Lee, \"A Unified Approach to Interpreting Model Predictions,\" Advances in Neural Information Processing Systems(NeurIPS), Vol. 30, pp. 4765-4774, 2017.",
 "[17] S. M. Lundberg and S.-I. Lee, \"A Unified Approach to Interpreting Model Predictions,\" Advances in Neural Information Processing Systems(NeurIPS), Vol. 30, pp. 4765-4774, Dec. 2017. https://doi.org/10.48550/arXiv.1705.07874"),

("[18] C. Rudin, \"Stop Explaining Black Box Machine Learning Models for High Stakes Decisions and Use Interpretable Models Instead,\" Nature Machine Intelligence, Vol. 1, No. 5, pp. 206-215, 2019.",
 "[18] C. Rudin, \"Stop Explaining Black Box Machine Learning Models for High Stakes Decisions and Use Interpretable Models Instead,\" Nature Machine Intelligence, Vol. 1, No. 5, pp. 206-215, May 2019. https://doi.org/10.1038/s42256-019-0048-x"),

("[19] A. Yang et al., \"Qwen2 Technical Report,\" arXiv preprint arXiv:2407.10671, 2024.",
 "[19] A. Yang et al., \"Qwen2 Technical Report,\" arXiv preprint arXiv:2407.10671, Jul. 2024. https://doi.org/10.48550/arXiv.2407.10671"),
]

def esc(s):
    return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

for old, new in REFS:
    o = esc(old)
    assert d.count(o) == 1, 'ref not found/unique: %r -> %d' % (old[:40], d.count(o))
    # 문단 전체를 찾아 stale linesegarray 제거(첫 줄만 유지)
    i = d.find(o)
    ps = d.rfind('<hp:p ', 0, i); pe = d.find('</hp:p>', i) + 7
    para = d[ps:pe].replace(o, esc(new))
    segs = re.findall(r'<hp:lineseg [^/]*?/>', para)
    if segs:
        para = re.sub(r'<hp:linesegarray>.*?</hp:linesegarray>',
                      '<hp:linesegarray>' + segs[0] + '</hp:linesegarray>', para, flags=re.S)
    d = d[:ps] + para + d[pe:]

open(SRC,'w',encoding='utf-8').write(d)
print('참고문헌 %d건 갱신 완료' % len(REFS))
