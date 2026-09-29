# 金融经济学每日文献速递（2026-09-29）

共筛选到 **12** 篇文献。

> 📢 **今日综述**
>
> 本期共收录 12 篇论文。研究方向主要集中在金融经济学（6 篇）、风险管理与衍生品（4 篇）、保险与养老（1 篇）。方法上以实验方法、优化方法为主。来源分布：OpenAlex（6 篇）、arXiv（5 篇）、Semantic Scholar（1 篇）。

## 1. Comparative Evaluation of Hyperparameter Optimization Strategies for k-Nearest Neighbors over Mixed Domain Search Spaces
- 来源：openalex
- 作者：Meta Kallista, Ig. Prasetya Dwi Wibawa, Heni Widayani
- 期刊/来源：CAUCHY Jurnal Matematika Murni dan Aplikasi
- 发表日期：2026-09-28
- 引用数：0
- 主题：Hyperparameter optimization, Hyperparameter, Categorical variable, Computer science, Artificial intelligence
- 链接：[DOI](https://doi.org/10.18860/cauchy.v11i2.42295) [链接](https://openalex.org/W7213548054)

**中文摘要（自动生成）**：【风险管理与衍生品】K-最近邻（KNN）算法因其简单性、可解释性和非参数特性而始终是一个强大的基线方法；然而，其预测性能对相互作用的超参数非常敏感。本文研究了在包含整数邻域大小、分类距离度量和连续Minkowski指数的混合搜索空间中，对KNN算法的超参数进行搜索受限优化。在统一的嵌套验证协议下，比较了七种调优策略：网格搜索、随机搜索、贝叶斯优化、遗传算法、粒子群优化和灰狼优化，并采用了标准化的预处理方法。实验使用了来自UCI、OpenML和Kaggle的多种公开分类数据集，评估了预测性能（准确率、宏观AUC、交叉熵）、验证损失和运行时间。结果表明，在有限的评估次数下，自适应优化器通常能提供比穷举搜索更优的性能-成本平衡；同时，没有一种方法在所有数据集上都表现一致最佳。基于秩的非参数统计比较进一步支持了观察到的差异，并为根据评估搜索方式和混合域搜索空间的特点选择调优策略提供了实际建议。。研究方法：贝叶斯方法、实验方法、优化方法。

## 2. Copula Regression for Deductible--Claim Dependence in Non-Life Insurance: A Stratified Evaluation
- 来源：openalex
- 作者：Dwi Mifta Mahanani, Feby Indriana Yusuf, Dzaki Ferlian Nugroho, Tuti Sariningsih Budi Utami
- 期刊/来源：CAUCHY Jurnal Matematika Murni dan Aplikasi
- 发表日期：2026-09-28
- 引用数：0
- 主题：Deductible, Econometrics, Actuarial science, Copula (linguistics), Mathematics
- 链接：[DOI](https://doi.org/10.18860/cauchy.v11i2.43524) [链接](https://openalex.org/W7213887025)

**中文摘要（自动生成）**：【保险与养老】在考虑了所有观测到的评级变量后，免赔额选择可能与理赔结果存在统计学上的关联。合同中的免赔额与作为连续工作边际使用的标准化免赔额比率有所不同；其中，理赔次数保持离散状态，而单个理赔的严重程度则保持连续性。通过“典型藤蔓对偶耦合”（Canonical Vine pair-copula）模型，将免赔额比率、理赔频率以及单个理赔的严重程度联系起来。本研究使用了2006年至2010年间威斯康星州地方政府财产保险基金（Wisconsin Local Government Property Insurance Fund）的1,038个案例数据进行建模，模型基于2006-2009年的数据估计，并通过2010年的数据进行了验证。研究发现：在免赔额与理赔频率的关系中存在负相关性；在免赔额与理赔严重程度的关系中存在正相关性；而在免赔额为条件的情况下，理赔频率与理赔严重程度之间存在负相关性。这些模式被解释为条件性关联，可能反映了选择效应和理赔报告机制的影响，而非逆向选择（adverse selection）或道德风险（moral hazard）的因果证据。该依赖性模型的对数评分在64.55%的频率观测值...。

## 3. FinAutoRubric: Expert-Guided Automatic Rubric Generation for Evaluating Financial Research Agents
- 来源：arxiv
- 作者：Hoyoung Lee, Suyeol Yun, Jack Haverty, Yunju Cho, Meesong Kim
- 期刊/来源：arXiv
- 发表日期：2026-09-28
- 引用数：0
- 主题：Economics, Finance
- 链接：[链接](http://arxiv.org/abs/2609.35744v1)

**中文摘要（自动生成）**：【金融经济学】评估金融研究代理需要使用能够反映专家标准的评分标准，并确保这些标准在信息截止日期前保持准确无误。经过专家评审的金融基准测试依赖于固定的、针对每个项目的评分标准，但这些标准的扩展成本较高，且无法体现每个机构自身的具体要求。在FinAutoRubric系统中，专家们制定了可重复使用的评估指南；而代理程序和代码则负责根据具体需求生成、审核和验证评分标准。这些专家指南以提示和规则的形式指导代理程序的工作，同时一套可重复使用的评估标准库（Task Bank）将这些指南应用于各种任务中。在遵循专家指导的长期循环过程中，撰写代理程序会研究每个预期结果，审核代理程序会对这些结果进行验证；如果出现错误，系统会自动将问题转交给人工处理。在三个由专家编写的金融基准测试中，FinAutoRubric的评分标准与最优秀的自动评分系统在评分结果上高度一致；此外，这些标准还明确了更多评估指标的预期得分范围，其评分结果与人工评分结果高度吻合。在内部分析师进行的盲评中，他们也更倾向于使用FinAutoRubric。基于78项任务和八类资产类别的内部分析师提出的关键问题开发的FinAutoRubric基准测试（包含...。

## 4. Optimal Networks for Agentic Information Aggregation
- 来源：arxiv
- 作者：MohammadHossein Bateni, Zahra Hadizadeh, MohammadTaghi Hajiaghayi, Mahdi JafariRaviz, Shayan Taherijam
- 期刊/来源：arXiv
- 发表日期：2026-09-28
- 引用数：0
- 主题：Economics, Finance
- 链接：[链接](http://arxiv.org/abs/2609.35537v1)

**中文摘要（自动生成）**：【金融经济学】我们研究了Kearns、Roth和Ryu（SODA 2026）提出的网络学习模型中的信息聚合机制。在该模型中，$d$个特征遵循某种固定分布，所有特征共享相同的标签。代理节点在有向无环图（DAG）上按拓扑顺序进行学习：每个代理节点观察部分特征及其父节点的预测结果，然后拟合一个线性预测模型以最小化均方误差，并仅将自己的预测结果传递给后续节点。全局预测模型则是利用所有特征得到的最优线性预测模型。Kearns、Roth和Ryu指出：在特征覆盖足够充分的情况下，通过足够深的路径传递预测结果，输出代理的预测误差会逐渐趋近于全局预测模型的误差；而路径深度不足则可能导致信息聚合无法在大型网络中实现。  

与他们主要关注给定图结构和特征分配的情况不同，我们探讨了该模型在两种不同设定下的极限行为。在第一种设定（“自适应设计者”设定）中，设计者事先知晓分布情况，可以自由选择图结构、特征分配方式以及输出代理节点的配置；而在第二种设定（“无知设计者”设定）中，设计者在对手选择分布之前就已固定了所有参数。每种情况下，每个代理节点仅观察一个特征，并从有限数量的父节点接收预测结果。  

当输出代理的预测结果...。

## 5. Climate Risk Exposure, Climate Policy Uncertainty, and Corporate Environmental Performance: Evidence from China
- 来源：semantic_scholar
- 作者：Xin-Yi Li, Fei Su, Qian-Yi Zhuang
- 期刊/来源：Journal of Transition Economics and Finance
- 发表日期：2026-09-25
- 引用数：0
- 主题：Environmental Science, Economics
- 链接：[DOI](https://doi.org/10.1142/s3082844926500119) [链接](https://api.semanticscholar.org/CorpusID:292397461)

**中文摘要（自动生成）**：【风险管理与衍生品】本文探讨企业气候风险暴露（Corporate Climate Risk Exposure, CRE）是否与更强的环境绩效相关，以及区域气候政策不确定性（Regional Climate Policy Uncertainty, CCPU）是否削弱了这种关联。通过分析2016至2024年间中国A股上市公司的面板数据，我们发现企业气候风险暴露与企业环境绩效呈正相关，而企业气候风险暴露与区域气候政策不确定性之间的交互作用显著为负。这一结论在采用不同的企业气候风险衡量指标、进行数据 Winsorization 处理、剔除异常上市状态的公司以及运用倾向得分匹配方法后依然成立。当区域气候政策不确定性通过极端寒冷天气作为工具变量，或者企业气候风险暴露通过同行业企业的平均信息披露水平作为工具变量时，该结果依然保持稳定。其中，华证环境评分（Huazheng Environmental Score）的相关性最为显著；而其他更广泛的ESG指标及替代性环境评估方法的支持力度相对有限，因此我们并不将这一发现视为适用于所有ESG维度的普遍现象。这种关联的减弱主要体现在那些调整空间较大的企业身上：规模较小、杠杆...。研究方法：面板数据。

## 6. Classification of Educational Vulnerability Status Using Boosting Methods on Imbalanced Socioeconomic Data
- 来源：openalex
- 作者：Andi Illa Erviani Nensi, Meavi Cintani, Mahda Al Maida, A. Qeis Tenridapi, Bagus Sartono
- 期刊/来源：CAUCHY Jurnal Matematika Murni dan Aplikasi
- 发表日期：2026-09-28
- 引用数：0
- 主题：Boosting (machine learning), Socioeconomic status, Machine learning, Feature selection, Artificial intelligence
- 链接：[DOI](https://doi.org/10.18860/cauchy.v11i2.39670) [链接](https://openalex.org/W7214477342)

**中文摘要（自动生成）**：【金融经济学】教育数据中极端的类别不平衡导致分类模型偏向多数类别，从而无法识别那些未上学的弱势学生，而这一群体恰恰最需要干预。本研究旨在开发一种分类模型，用于识别学龄儿童的教育脆弱性状况。其中，“正类”对应于失学儿童（少数类别），“负类”则代表仍在上学的儿童。该数据集的类别不平衡比例高达约1:48，使得传统的分类方法无法有效检测到少数类别的样本。为了解决这一问题，研究人员比较了四种具有类别不平衡感知能力的提升算法：AdaBoost-M2、SMOTEBoost、RBBoost和RUSBoost。模型选择通过训练集的分层五折交叉验证进行，随后在独立测试集上进行最终评估。评估指标包括敏感性、特异性、平衡准确率和曲线下面积（AUC），这些指标对于高度不平衡的数据更为适用。结果表明，当阈值设为0.50时，SMOTEBoost L50算法取得了最高的平衡准确率（0.7474）、敏感性（0.8824）和AUC（0.7745）。然而，其少数类别的精确度（0.0452）和F1分数（0.0860）较低，表明在提高检测率的同时存在较大的误报风险。这些发现表明，将少数类别平衡策略与提升算法相结合可以显著提升在高度不平...。

## 7. Riding the Wave of the Global Minimum Tax Regime: The Rise and (Potential) Transformation of Super Deductions for Research and Development (R&D) Expenses in Asia
- 来源：openalex
- 作者：Duc Tam Nguyen The, Tai Chu Anh
- 期刊/来源：Intertax
- 发表日期：2026-09-28
- 引用数：0
- 主题：Incentive, Pillar, Tax incentive, Economics, Business
- 链接：[DOI](https://doi.org/10.54648/taxi2026070) [链接](https://openalex.org/W7214516653)

**中文摘要（自动生成）**：【金融经济学】本文研究了五个亚洲经济体（中国、香港、印度、印度尼西亚和新加坡）的创新生态系统的演变过程，重点探讨了超额抵扣（Super Deduction, SD）制度在促进研发投资、增强国内技术实力以及吸引外资方面所起的作用。这些机制对于这些经济体的发展至关重要，也使它们成为重要的创新中心。本研究采用了发展中国家（尤其是资本输入型亚洲经济体）的视角，与主流文献中关注发达国家的观点形成对比。在这种视角下，税收激励措施主要被视为促进发展的工具，而非导致税基侵蚀的根源。然而，经济合作与发展组织（OECD）/二十国集团（G20）提出的“全球反税基侵蚀”（Global Anti-Base Erosion, GloBE）规则对税收激励的有效性提出了挑战，因为这些激励措施可能会被附加税所抵消。文章分析了超额抵扣制度与全球最低税标准之间的矛盾，评估了相关企业的合规成本和制度负担。最后，本文认为这些经济体必须重新设计税收激励措施，以符合全球反税基侵蚀规则的要求，从而保持竞争力并实现持续的技术进步。。

## 8. PENGARUH PENGHINDARAN PAJAK, STRUKTUR KEPEMILIKAN, DAN FAKTOR LAINNYA TERHADAP NILAI PERUSAHAAN
- 来源：openalex
- 作者：Merieska Magdalena Putri, Umar Issa Zubaidi
- 期刊/来源：E-Jurnal Akuntansi TSM
- 发表日期：2026-09-28
- 引用数：0
- 主题：Stock exchange, Enterprise value, Business, Profitability index, Leverage (statistics)
- 链接：[DOI](https://doi.org/10.34208/ejatsm.v6i3.3443) [链接](https://openalex.org/W7214517331)

**中文摘要（自动生成）**：【金融经济学】企业价值反映了公司的经营绩效和未来发展潜力，这些因素取决于公司在特定时期内的运营状况。本研究旨在通过实证分析，探讨避税行为、董事会规模、机构所有权、外资持股比例、性别多样性、盈利能力、企业规模以及杠杆率对企价值（以托宾Q值衡量）的影响。研究选取了2022年至2024年间在印度尼西亚证券交易所（IDX）上市的制造业公司作为样本，采用目的性抽样方法进行数据收集，并运用多元回归分析方法对数据进行处理。最终共有133家公司被纳入研究范围，共计399个观测值。研究结果表明，盈利能力与杠杆率对企价值具有正向促进作用，而企业规模则对企价值产生负面影响；相比之下，避税行为、董事会规模、机构所有权、外资持股比例以及性别多样性对企价值的影响并不显著。这些发现表明，在评估企业价值时，投资者更关注公司的财务表现和资本结构，而非治理结构或所有权特征。。研究方法：回归分析。

## 9. BiLSTM-Based Deep Learning Model for Early Prediction of Student Academic Failure Risk in Digital and Distance Education
- 来源：openalex
- 作者：Liza Yuliana, Liesma M. Siregar
- 期刊/来源：JOURNAL OF DIGITAL LEARNING AND DISTANCE EDUCATION
- 发表日期：2026-09-28
- 引用数：0
- 主题：Distance education, Deep learning, Dropout (neural networks), Computer science, Recall
- 链接：[DOI](https://doi.org/10.56778/jdlde.v5i4.780) [链接](https://openalex.org/W7214518766)

**中文摘要（自动生成）**：【风险管理与衍生品】数字和远程学习平台会生成大量来自学生的交互日志数据。然而，由于时间敏感性和远程学习环境中的序列数据处理问题，利用这些时间日志数据来提前预测学生的学业失败风险仍然具有挑战性。本研究旨在基于双向长短期记忆网络（BiLSTM）开发一种深度学习模型，通过分析学习管理系统（LMS）中的每周交互模式来预测学生的学业表现和失败风险。研究分析了1,250名远程教育学生在一个学期内的交互日志数据，提取了诸如材料访问频率、论坛参与度和作业提交时间等特征。实验结果表明，该BiLSTM模型在课程进行到第6周时，准确率达到了91.4%，精确率为89.2%，召回率为92.6%。这种早期预测机制使教育工作者能够及时采取教学干预措施，从而降低数字和远程学习环境中的学生辍学率。。研究方法：深度学习、实验方法。

## 10. Representation Risk in Pretrained Image Encoders
- 来源：arxiv
- 作者：Morgan Nordstrom, Vamuyan Sesay, Matthew D. Webb
- 期刊/来源：arXiv
- 发表日期：2026-09-28
- 引用数：0
- 主题：Economics, Finance
- 链接：[链接](http://arxiv.org/abs/2609.35470v1)

**中文摘要（自动生成）**：【风险管理与衍生品】应用研究人员越来越多地使用预训练的编码器将图像转换为特征，然后在下游预测模型中利用这些特征。编码器通常被视为实现细节，但我们认为它实际上是模型不确定性的一个重要来源。我们将这种不确定性称为“表示风险”：合理的预训练编码器可能会将相同的图像映射到不同的特征空间，从而导致样本外预测结果的显著差异。我们对比了十种现代编码器和传统编码器在多种应用中的表现，这些应用包括房价预测、赛马性能分析、乳腺癌组织学研究、胸部X光图像分析、面部年龄连续估计以及水稻病害检测。通过采用常见的维度控制方法、数据分组策略以及分组安全的验证方法，我们发现SigLIP 2在房价预测任务中的表现显著提升（$R^2$从ResNet50的0.396提高到了0.629），DINOv2在赛马性能分析中的$R^2$从0.029提高到了0.105。没有一种编码器能在所有任务中都表现出最佳性能。我们使用训练数据构建了多种候选算法，并在独立的验证数据集上进行了测试。最终选定的算法在房价预测任务中的准确率为0.658，在肺炎检测任务中的准确率为0.979。对于赛马和水稻病害分析，固定数据分组的改进效果较为有限；而重复数据分组则揭示了...。

## 11. AI-based matching improves refugee employment in a double-blind randomized trial
- 来源：arxiv
- 作者：Kirk Bansak, Jens Hainmueller, Dominik Hangartner, Jeremy Ferwerda, Elisabeth Paulson
- 期刊/来源：arXiv
- 发表日期：2026-09-28
- 引用数：0
- 主题：Economics, Finance
- 链接：[链接](http://arxiv.org/abs/2609.35448v1)

**中文摘要（自动生成）**：【劳动经济学】难民的融入是接收国面临的核心政策挑战，政府最初对难民的安置方式会直接影响其融入进程。然而，安置官员往往对每个难民案例最有可能成功的安置地点了解有限。基于算法的难民安置系统利用行政数据、机器学习及约束优化技术，在难民到达时实时推荐最有利于就业的安置方案，最终安置决策仍由人工安置官员作出。2020年1月至2023年6月期间，瑞士移民事务部随机将约2000名难民案例分配到不同州进行安置：其中一部分案例通过算法优化后得到就业推荐，另一部分则按照现有程序进行分配；在分配过程中，安置官员和难民均对具体分配结果不知情。这两种安置方式使用了相同但独立的州和原籍群体配额标准，因此观察到的效果主要反映了难民与安置州之间的匹配程度，而非难民被重新分配到劳动力市场更为强劲的地区。该试验开始于新冠疫情之前，当时劳动力市场状况尚未发生显著变化。

对于主要评估指标——难民在前三年的就业月数占比——2020年至2023年各安置组别的意向治疗（ITT）估计值为+2.2个百分点（占对照组平均水平的10%；95%置信区间为[+0.05, +4.33]）；而在2022年至2023年的新冠疫情后时期，这一数值上升至+3...。研究方法：机器学习、优化方法。

## 12. From Cointegration to Out-of-Sample Failure: A Pairs-Trading Case Study on PEP-KO
- 来源：arxiv
- 作者：Davide Graziano
- 期刊/来源：arXiv
- 发表日期：2026-09-28
- 引用数：0
- 主题：Economics, Finance
- 链接：[链接](http://arxiv.org/abs/2609.35359v1)

**中文摘要（自动生成）**：【金融经济学】本文研究了基于协整关系的百事公司与可口可乐公司之间的配对交易策略在统计上的稳健性及其经济可行性。首先，我们对2013至2018年期间的数据进行了协整性检验，并估计了价差的平均回归特征；随后在保持这些统计参数不变的情况下，对2018至2023年期间的样本数据进行了基于阈值的交易策略优化。通过交易成本敏感性测试、参数敏感性测试、滚动OLS（Ordinary Least Squares）方法以及卡尔曼滤波器（Kalman Filter）对策略的稳健性进行了评估。最后，我们将该策略应用于2023年至今的样本外数据，包括使用滚动OLS方法和卡尔曼滤波器分析时变对冲比率。研究结果表明，价差的平均回归特征减弱降低了该策略在样本外时期的有效性。。研究方法：协整分析。
