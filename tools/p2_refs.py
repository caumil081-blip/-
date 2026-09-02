# -*- coding: utf-8 -*-
"""2번 논문 참고문헌: 발행 월 + DOI + KIIT 양식 표기법(따옴표 뒤 쉼표, 월 약어)."""
import re, sys
sys.path.insert(0, '.')
import relayout as R

S = 'ex/Contents/section0.xml'
d = open(S, encoding='utf-8').read()
def esc(s): return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

REFS = [
("[1] E. Rahm and P. A. Bernstein, \"A survey of approaches to automatic schema matching,\" The VLDB Journal, Vol. 10, No. 4, pp. 334-350, 2001.",
 "[1] E. Rahm and P. A. Bernstein, \"A survey of approaches to automatic schema matching\", The VLDB Journal, Vol. 10, No. 4, pp. 334-350, Dec. 2001. https://doi.org/10.1007/s007780100057."),
("[2] J. Madhavan, P. A. Bernstein, and E. Rahm, \"Generic schema matching with Cupid,\" Proceedings of the International Conference on Very Large Data Bases(VLDB), pp. 49-58, 2001.",
 "[2] J. Madhavan, P. A. Bernstein, and E. Rahm, \"Generic schema matching with Cupid\", Proc. of the Int. Conf. on Very Large Data Bases(VLDB), Roma, Italy, pp. 49-58, Sept. 2001. https://doi.org/10.5555/645927.672191."),
("[3] H. H. Do and E. Rahm, \"COMA: A system for flexible combination of schema matching approaches,\" Proceedings of the International Conference on Very Large Data Bases(VLDB), pp. 610-621, 2002.",
 "[3] H. H. Do and E. Rahm, \"COMA: A system for flexible combination of schema matching approaches\", Proc. of the Int. Conf. on Very Large Data Bases(VLDB), Hong Kong, China, pp. 610-621, Aug. 2002. https://doi.org/10.1016/B978-155860869-6/50060-3."),
("[4] J. Devlin, M.-W. Chang, K. Lee, and K. Toutanova, \"BERT: Pre-training of deep bidirectional transformers for language understanding,\" Proceedings of the Conference of the North American Chapter of the Association for Computational Linguistics(NAACL-HLT), pp. 4171-4186, 2019.",
 "[4] J. Devlin, M.-W. Chang, K. Lee, and K. Toutanova, \"BERT: Pre-training of deep bidirectional transformers for language understanding\", Proc. of NAACL-HLT, Minneapolis, MN, USA, pp. 4171-4186, June 2019. https://doi.org/10.18653/v1/N19-1423."),
("[5] N. Reimers and I. Gurevych, \"Sentence-BERT: Sentence embeddings using Siamese BERT-networks,\" Proceedings of the Conference on Empirical Methods in Natural Language Processing(EMNLP-IJCNLP), pp. 3982-3992, 2019.",
 "[5] N. Reimers and I. Gurevych, \"Sentence-BERT: Sentence embeddings using Siamese BERT-networks\", Proc. of the Conf. on Empirical Methods in Natural Language Processing(EMNLP-IJCNLP), Hong Kong, China, pp. 3982-3992, Nov. 2019. https://doi.org/10.18653/v1/D19-1410."),
("[6] A. Narayan, I. Chami, L. Orr, and C. Ré, \"Can foundation models wrangle your data?,\" Proceedings of the VLDB Endowment, Vol. 16, No. 4, pp. 738-746, 2022.",
 "[6] A. Narayan, I. Chami, L. Orr, and C. Ré, \"Can foundation models wrangle your data?\", Proceedings of the VLDB Endowment, Vol. 16, No. 4, pp. 738-746, Dec. 2022. https://doi.org/10.14778/3574245.3574258."),
("[7] R. Peeters and C. Bizer, \"Entity matching using large language models,\" arXiv preprint arXiv:2310.11244, 2023.",
 "[7] R. Peeters and C. Bizer, \"Entity matching using large language models\", arXiv preprint arXiv:2310.11244, Oct. 2023. https://doi.org/10.48550/arXiv.2310.11244."),
("[8] B. Settles, \"Active learning literature survey,\" University of Wisconsin-Madison, Tech. Rep. 1648, 2009.",
 "[8] B. Settles, \"Active learning literature survey\", Computer Sciences Technical Report 1648, University of Wisconsin-Madison, Jan. 2009."),
("[9] C. H. Yu, G. D. Jung, and T. J. Son, \"A Proposal of MND's Interoperability Policies by Adopting the SOSI Model Concepts,\" The Quarterly Journal of Defense Policy Studies, Vol. 27, No. 3, pp. 67-105, 2011. (in Korean)",
 "[9] C. H. Yu, G. D. Jung, and T. J. Son, \"A Proposal of MND's Interoperability Policies by Adopting the SOSI Model Concepts\", The Quarterly Journal of Defense Policy Studies, Vol. 27, No. 3, pp. 67-105, Sept. 2011. https://doi.org/10.22883/jdps.2011.27.3.003. (in Korean)"),
("[10] K. Y. Kim, D. Kim, H. Son, and M. Sohn, \"Study on the Integration Method of Defense Command and Control Data based on Layered Ontologies and Knowledge Graphs,\" Journal of Internet Computing and Services, Vol. 26, No. 1, pp. 193-202, 2025. (in Korean)",
 "[10] K. Y. Kim, D. Kim, H. Son, and M. Sohn, \"Study on the Integration Method of Defense Command and Control Data based on Layered Ontologies and Knowledge Graphs\", Journal of Internet Computing and Services, Vol. 26, No. 1, pp. 193-202, Feb. 2025. https://doi.org/10.7472/jksii.2025.26.1.193. (in Korean)"),
]
for old, new in REFS:
    o = esc(old)
    assert d.count(o) == 1, '참고문헌 못 찾음/중복: %r -> %d' % (old[:45], d.count(o))
    d = d.replace(o, esc(new))
open(S, 'w', encoding='utf-8').write(d)
print('참고문헌 %d건 정비 (월 + DOI + 따옴표 뒤 쉼표)' % len(REFS))
for s, e in R.paragraphs(d):
    t = R.own_text(d[s:e]).strip()
    if re.match(r'^\[\d+\]', t): print('  ' + t[:150])
