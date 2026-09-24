# 金融经济学每日文献速递（2026-09-24）

共筛选到 **3** 篇文献。

> 📢 **今日综述**
>
> 本期共收录 3 篇论文。研究方向主要集中在金融经济学（3 篇）。方法上以神经网络、Transformer 模型为主。来源分布：OpenAlex（2 篇）、Semantic Scholar（1 篇）。其中 1 篇命中顶级期刊白名单。

## 1. Numerical Investigation of Sequence Modeling Theory using Controllable Memory Functions
- 来源：openalex
- 作者：Haotian Jiang, Zeyu Bao, Shida Wang, Qianxiao Li
- 期刊/来源：Journal of Machine Learning
- 发表日期：2026-09-23
- 引用数：0
- 主题：Computer science, Sequence (biology), Transformer, Artificial intelligence, Function (biology)
- 链接：[DOI](https://doi.org/10.4208/jml.251216) [链接](https://openalex.org/W4417114785)

**中文摘要（自动生成）**：【金融经济学】序列建模架构的演变，从循环神经网络和卷积模型发展到Transformer和结构化状态空间模型，反映了人们为解决序列数据中固有的多种时间依赖性而持续做出的努力。尽管取得了这些进展，但系统地描述这些架构的优势和局限性仍然是一个根本性的挑战。在这项工作中，我们提出了一个合成基准测试框架，用于评估不同序列模型捕捉不同时间结构的有效性。该方法的核心是生成合成目标数据，每个目标都由一个参数化的记忆函数$\rho(s, \alpha)$和一个可控参数$\alpha$来表征，该参数决定了时间依赖性的强度。这种设置使我们能够生成一系列时间复杂度各异的任务，从而能够针对特定的记忆属性对模型行为进行细致的分析。我们重点研究了四种代表性的记忆函数，每种函数对应于一类不同的时间结构：指数函数和多项式函数用于描述衰减动态，脉冲函数用于表示长距离依赖性，而Airy函数用于描述稀疏模式。在多种序列建模架构上的实验验证了现有的理论见解，并揭示了关于逼近能力、优化动态和架构权衡的新发现。这些结果证明了所提出方法在推进理论理解方面的有效性，并强调了使用具有明确定义结构的可控目标数据来评估序列建模架构的重要性。。研究方法：神经网络、Transformer 模型、实验方法、优化方法。

## 2. Explainable deep learning-based classification of Wolff-Parkinson-White electrocardiographic signals
- 来源：openalex
- 作者：Alice Ragonesi, Stefania Fresca, Karli Gillette, Stefan Kurath-Koller, Gernot Plank
- 期刊/来源：Frontiers in Physiology
- 发表日期：2026-09-23
- 引用数：0
- 主题：Artificial intelligence, Ventricular tachycardia, Computer science, Cardiac electrophysiology, Deep learning
- 链接：[DOI](https://doi.org/10.3389/fphys.2026.1855555) [链接](https://openalex.org/W7105135027)

**中文摘要（自动生成）**：【金融经济学】引言  
Wolff-Parkinson-White（WPW）综合征是一种心脏电生理（EP）疾病，其病因在于存在一条旁路（AP），该旁路绕过了房室结，导致心室激活速度加快，并为房室折返性心动过速（AVRT）的发生提供了条件。准确定位旁路对于制定和指导导管消融手术至关重要。虽然传统的诊断树（DT）方法和较新的机器学习（ML）技术已被提出用于根据体表心电图（ECG）预测旁路位置，但这些方法往往受到解剖定位分辨率有限、解释性差以及临床数据集规模较小的限制。  

方法  
在这项初步的、针对特定患者的研究中，我们开发了一种深度学习（DL）模型，用于在24个心脏区域中定位单一的明显旁路。该模型基于一个包含大量生理学上真实数据的合成ECG数据库进行训练，这些数据是通过使用个性化的虚拟心脏模型生成的。此外，我们还将可解释人工智能（XAI）技术（包括引导反向传播、Grad-CAM和Guided Grad-CAM）整合到该模型中，从而实现了对DL决策过程的解释，解决了机器学习预测缺乏透明性的主要障碍。  

结果  
在所研究的单一心脏几何结构中，该模型的定位准确率超过了94%，平均F1分数超过...。研究方法：机器学习、深度学习。

## 3. The Role of Stock Markets in Economic Growth: Empirical Evidence From Panel Data Analysis
- 来源：semantic_scholar
- 作者：İshak Demir
- 期刊/来源：International Journal of Finance & Economics
- 发表日期：2026-09-21
- 引用数：1
- 主题：Economics
- 链接：[DOI](https://doi.org/10.1002/ijfe.70303) [链接](https://api.semanticscholar.org/CorpusID:292235666)

**中文摘要（自动生成）**：【金融经济学】股市发展被广泛视为经济表现的重要组成部分，它影响着经济体如何调动资本、配置资源以及支持长期增长。本研究利用2003年至2022年间36个国家的季度面板数据，探讨了股市发展与经济增长之间的联系。通过运用面板协整检验、完全修正的OLS（Ordinary Least Squares）模型以及面板向量误差修正（Panel Vector Error Correction, VECM）框架，我们分析了这种关系的长期与短期动态。研究发现，股市资本化与经济增长之间存在正向且显著的长期关联，且在高收入经济体中这种效应更为显著。在高收入国家，短期因果关系是双向的；而在低收入和中等收入国家，这种关系仅表现为股市发展促进经济增长。基于金融成熟度的内生性划分，阈值面板VECM模型表明，市场调整过程具有非线性特征，并且取决于各国的金融发展水平。研究结果表明，金融发展水平较低的经济体可以通过加强市场制度、提高市场流动性以及提升监管质量来更好地发挥股市对经济增长的促进作用。。研究方法：协整分析、误差修正模型。
