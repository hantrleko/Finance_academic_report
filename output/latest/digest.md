# 金融经济学每日文献速递（2026-11-18）

共筛选到 **12** 篇文献。

> 📢 **今日综述**
>
> 本期共收录 12 篇论文。研究方向主要集中在金融经济学（10 篇）、房地产金融（1 篇）、行为金融（1 篇）。方法上以实验方法、随机实验为主。来源分布：arXiv（6 篇）、OpenAlex（3 篇）、NBER（2 篇）。其中 2 篇命中顶级期刊白名单。

## 1. Phase Transition in Binary Compressed Sensing via Annealing with Adaptive Regularization
- 来源：openalex
- 作者：Xiaoxin Huang, Masayuki Ohzeki
- 期刊/来源：Journal of the Physical Society of Japan
- 发表日期：2026-11-17
- 引用数：0
- 主题：Binary number, Regularization (linguistics), Algorithm, Computer science, Quadratic equation
- 链接：[DOI](https://doi.org/10.7566/jpsj.95.124006) [链接](https://openalex.org/W7127043528)

**中文摘要（自动生成）**：【金融经济学】正则化选择会改变基于退火算法的二元压缩感知的恢复相图。我们提出了一种正则化选择方法，该方法结合了系统化的参数搜索与随机森林回归技术。在噪声为零的高斯测量环境下，且已知数据具有稀疏性时，通过多次模拟退火（SA）试验，从候选参数网格中选取最优参考参数，这些参数是通过最小化均方重建误差来确定的。所建立的模型能够根据信号维度、采样比例和数据稀疏性预测这些参考值。在已知正则化参数的情况下，模拟退火算法的恢复过程在较大信号维度下大致遵循盒约束条件下的渐进参考边界。如果不进行重新训练，相同的预测器可以为模拟退火算法和量子-经典混合求解器提供相同的正则化参数。在匹配的问题实例中，混合求解器在评估的参数空间部分区域内能够实现比模拟退火算法更低的均方重建误差。该规则能够重用已搜索到的信息进行后续重建，而无需在每个设置下都重复进行参数搜索。研究结果量化了在特定有限候选参数网格和求解器设置下的实际性能表现，但这些结果并不构成对求解器独立性的保证，也不涉及求解时间上的比较。。研究方法：回归分析、随机森林。

## 2. Improving FMQA via Initial Training Data Design Considering Marginal Bit Coverage in One-Hot Encoding
- 来源：openalex
- 作者：Taiga Hayashi, Yuya Seki, Kotaro Terada, Yosuke Mukasa, Shuta Kikuchi
- 期刊/来源：Journal of the Physical Society of Japan
- 发表日期：2026-11-17
- 引用数：1
- 主题：Latin hypercube sampling, Encoding (memory), Computer science, Algorithm, Binary data
- 链接：[DOI](https://doi.org/10.7566/jpsj.95.124005) [链接](https://openalex.org/W7160549366)

**中文摘要（自动生成）**：【金融经济学】基于二次优化退火（FMQA）的因子分解机是一种黑盒优化方法，它将因子分解机（FM）模型与基于二次无约束二进制优化（QUBO）的搜索算法相结合，其中QUBO部分通过伊辛机（Ising machine）来实现。当FMQA应用于通过独热编码（one-hot encoding）表示的整数或离散连续变量时，均匀随机初始采样可能导致许多二进制变量在训练数据中始终处于非激活状态，从而导致相应的FM参数无法从观测到的响应中获取到直接的梯度更新。为了解决这一问题，我们设计了初始训练数据，以确保所有通过独热编码生成的二进制变量至少出现过一次“1”的值，即实现完全的边际比特覆盖（complete marginal bit coverage）。我们采用了两种空间填充采样方法：拉丁超立方采样（Latin hypercube sampling，简称LHS）和Sobol序列（Sobol’ sequence），分别得到了LHS-FMQA和Sobol’-FMQA两种改进版本。在包含17个和32个设计变量的飞机机翼形状优化基准测试中，这两种改进方法均显著提高了最终巡航速度的平均数值，尤其在32变量问题上的优势更为明显。。研究方法：优化方法。

## 3. Inference after coding agents
- 来源：arxiv
- 作者：Florian Gunsilius, David Van Dijcke, Kaspar Wüthrich
- 期刊/来源：arXiv
- 发表日期：2026-11-17
- 引用数：0
- 主题：Economics, Finance
- 链接：[链接](http://arxiv.org/abs/2611.23174v1)

**中文摘要（自动生成）**：【金融经济学】随着人工智能编码代理在实证研究的各个环节（从编写代码到数据处理）中变得越来越熟练，实证研究正在迅速发生变化。我们认为，尽管编码代理在科学领域的应用潜力巨大，但它们在假设检验中的使用对传统推理方法构成了严重威胁，因为这些代理使得选择性推理的过程变得更加高效。具体而言，这些编码代理在进行实证研究时引入了一种新型的“后选择推理”机制：这种机制结合了人类式的开放式估计器搜索方式，以及选择和估计过程的程序化可重复性。在模拟数据中（即不存在实际效应的情况下），当要求这些代理得出具有说服力的研究结果时，有四种先进的编码代理在54%到98%的时间内报告了显著的p值。我们提出了一种简单的程序来检测和纠正这种偏差。在代理完成分析后，我们会重新设置数据并重新运行分析过程，以估计该代理在统计上“有利”的情况下选择该分析结果的概率。对于选择行为稳定的代理，经过校正后的检验在条件选择假设下是渐近有效的且具有一致性的。重要的是，这种校正方法是基于代理的实际选择行为进行学习的，而非基于对其搜索机制的建模；因此，即使人工智能技术持续快速发展，该方法依然有效。在模拟实验中，这种校正方法能够将较高的误拒绝率有效降低到...。研究方法：数值模拟。

## 4. Which Past Matters? Training History and Multi-Forecast Horizon in Equity Transformers
- 来源：arxiv
- 作者：Chariton Chalvatzis
- 期刊/来源：arXiv
- 发表日期：2026-11-17
- 引用数：0
- 主题：Economics, Finance
- 链接：[链接](http://arxiv.org/abs/2611.23126v1)

**中文摘要（自动生成）**：【金融经济学】更多的历史数据可以提高预测的准确性，但同时也会引入一些与当前市场状况关联较弱的因素。因此，我们研究了训练数据量与历史数据选择方式如何影响日内股票价格预测的预测范围（即预测时间跨度）。我们设计了十二种不同的模型配置，每种配置结合了四种采样和验证策略，并使用了6个月、12个月或24个月的训练数据量，这些模型均基于相同的横截面Transformer结构和特征集。通过每月进行一次滚动预测实验，我们获得了264次模型重新训练结果以及从5分钟到120分钟不等的累计收益预测数据。评估时间范围为2025年1月至2026年10月20日，评估方法采用了横截面Spearman信息系数来衡量模型对未来五因子残差收益的预测能力。结果显示：在5至15分钟的预测时间范围内，基于最近六个月数据的模型表现最佳；在20至30分钟的预测时间范围内，采用多种历史数据选择的模型表现更优；而在60至120分钟的预测时间范围内，均匀选择历史数据的模型表现最佳。虽然增加训练数据量并不能普遍提升预测准确性，但在15分钟、20分钟和25分钟的预测时间范围内，由所有十二个模型组成的加权集成模型的预测效果优于任何一个单独模型的预测结果...。研究方法：横截面分析、Transformer 模型、实验方法。

## 5. FROM GENERATED INFORMATION TO INTERNATIONALIZATION KNOWLEDGE: GENERATIVE AI, ABSORPTIVE CAPACITY AND SMES’ MARKET ENTRY DECISIONS
- 来源：semantic_scholar
- 作者：A. Diachkova
- 期刊/来源：Journal of Trends in Finance and Economics
- 发表日期：2026-11-13
- 引用数：0
- 主题：Business, Computer Science, Economics
- 链接：[DOI](https://doi.org/10.61784/jtfe3087) [链接](https://api.semanticscholar.org/CorpusID:295918014)

**中文摘要（自动生成）**：【金融经济学】生成式人工智能（GenAI）能够降低中小企业获取海外市场信息的相关成本，并为其制定替代性经营策略提供支持。然而，信息的丰富性并不必然提升决策质量。本文采用叙事性文献综述的方法，以吸收能力（absorptive capacity）作为主要理论视角，并结合乌普萨拉国际化过程模型（Uppsala Internationalization Process Model），探讨了经验知识与商业网络在国际化决策中的作用。研究的分析单元是指特定市场进入决策，这些决策涉及明确的产品、目标市场及进入模式。文章区分了信息处理效率、决策质量与企业绩效三个关键维度，指出生成的内容需要经过价值认定、证据验证及情境整合才能为决策提供有效支持。适当的资源投入及实践中的反馈有助于可复用知识的形成。这些过程是通过反馈机制相互关联的，而非遵循固定的线性顺序。GenAI的战略价值取决于信息生成速度与组织验证能力之间的匹配程度、难以编码的隐性知识在交易关系中的体现，以及反馈如何被纳入组织日常运作中。文章提出了三项研究命题，分别涉及信息扩展带来的研究负担、直接市场互动的必要性，以及保留记录对组织学习的支持条件。通过明确未来...。

## 6. Measuring the Impact of Impact Measurement
- 来源：nber
- 作者：Emanuele Colonnelli, Timothy McQuade, Natalia Rigol, Benjamin N. Roth
- 期刊/来源：NBER Working Papers
- 发表日期：
- 引用数：0
- 主题：Economics, Finance
- 链接：[链接](https://www.nber.org/papers/w36009#fromrss)

**中文摘要（自动生成）**：📌 研究问题：影响测量在社会创业和影响力投资中占据核心地位，但企业是否真正从测量影响中获益尚不明确。

🔬 研究方法：本研究在印度高增长社会企业中实施了首次随机对照试验（RCT），并在配套实验中测试了早期投资者对量化与定性影响陈述的反应。

📊 核心发现：接受干预的企业其收入增长和融资额几乎是对照组的两倍；同时，早期投资者对量化的影响指标反应强烈，而对通用的定性影响陈述反应冷淡。

💡 应用价值：研究结果表明，影响测量能够显著影响企业增长和资本配置。

## 7. Gambling for Goals
- 来源：nber
- 作者：Costas Arkolakis, Spencer Y. Kwon, Dominic Russel, Claire Shi, Hyunjoo Yang
- 期刊/来源：NBER Working Papers
- 发表日期：
- 引用数：0
- 主题：Economics, Finance
- 链接：[链接](https://www.nber.org/papers/w36010#fromrss)

**中文摘要（自动生成）**：【金融经济学】近年来，发达经济体的年轻人对自身经济前景的悲观情绪日益加剧。与此同时，类似赌博的金融活动也呈激增趋势。我们通过弗里德曼-萨维奇（Friedman-Savage，1948）提出的动机理论来解释这两种现象：当购房或结婚等人生目标看似遥不可及时，人们便会转向金融投机行为。我们利用一项原创调查数据，结合韩国主要征信机构、电信公司和信用卡发行机构的海量关联记录，对这一理论进行了验证。研究结果与理论预测一致：那些更重视难以实现的目标的人更倾向于承担风险，且他们所承担的风险类型会随着其与目标之间的距离而系统性变化。在个体层面，失业期间加密货币应用程序的使用率会上升，而通过抽奖获得价格受监管的住房购买资格后，这一使用率又会下降。进一步的研究表明，难以实现的目标会促使人们更加坚信自己的判断，从而放大过度乐观所带来的负面后果。。研究方法：模型校准、调查数据。

## 8. Firefly-Geni: Automated Iteration-Guided Generative Discovery of Thermally Activated Delayed Fluorescence Molecules
- 来源：openalex
- 作者：Boyuan Zhang, Xuerui Fang, De Yang, Yue Wang, Liu Y
- 期刊/来源：ACS Central Science
- 发表日期：2026-11-17
- 引用数：0
- 主题：Interpretability, Computer science, ENCODE, Property (philosophy), Generative grammar
- 链接：[DOI](https://doi.org/10.1021/acscentsci.6c01736) [链接](https://openalex.org/W7167016259)

**中文摘要（自动生成）**：【房地产金融】摘要  
热激活延迟荧光（TADF）分子的高效发现仍主要依赖于专家制定的设计规则，而文献中积累的大量结构-性质知识大多分散且未得到充分利用。在此，我们提出了Firefly-Geni这一自动化且可解释的活性分子进化框架，该框架通过闭环工作流程将分散的文献知识转化为结构新颖的TADF候选分子。Firefly-Geni整合了大型语言模型（LLM）辅助的数据提取、多任务性质预测、条件分子生成和理论评估功能。其数据挖掘模块将非结构化的文献信息转化为经过整理的实验性质数据库。该系统结合了双分子图多任务预测器和条件生成器，并引入量子化学反馈机制，从而实现结构新颖性的迭代优化。在单重态-三重态能量差ΔEST为0.05 eV、合成可及性（SA）评分为2.5的目标条件下，Firefly-Geni从10万个候选分子中筛选出了100个结构新颖的分子，这些分子经计算预测具有反向体系间跃迁能力且易于合成，覆盖了多种发射波长。其中一个合成得到的候选分子在氮气氛围下的实验ΔEST为0.019 eV，薄膜光致发光量子产率（PLQY）达到84%，与预测结果高度一致。可解释性分析进一步揭示了具有化学意义的结构-性质关...。研究方法：实验方法。

## 9. Integrating market sentiments for stock price prediction: A comparative study of Bi-LSTM and multilayer perceptions
- 来源：arxiv
- 作者：Ahmet Akusta
- 期刊/来源：arXiv
- 发表日期：2026-11-17
- 引用数：0
- 主题：Economics, Finance
- 链接：[链接](http://arxiv.org/abs/2611.23057v1)

**中文摘要（自动生成）**：【行为金融】本研究探讨了将情感分析技术与机器学习模型相结合，以预测股票价格走势的方法，并以Nvidia公司作为案例进行研究。情感评分是通过两种情感分析工具从与Nvidia相关的财经新闻标题中提取的：一种是专门针对金融领域的FinBERT工具，另一种是通用的情感分析工具TextBlob。这些评分被整合到基于双向长短期记忆网络（Bi-LSTM）和多层感知器（MLP）的预测框架中，同时结合了历史股票价格数据。研究评估了在整个观察期间以及不同市场阶段（牛市、市场停滞期和强劲牛市）中的预测性能。研究结果表明，在特定情境下，情感特征能够提升预测准确性，尤其是在市场停滞期，其中TextBlob在某些场景中的表现优于FinBERT。此外，与MLP相比，Bi-LSTM模型在捕捉时间序列依赖性方面表现出更强的能力。然而，在市场趋势明显的情况下（如强劲的牛市），情感特征的影响会减弱。在同一数据集中同时使用FinBERT和TextBlob能够从两个角度进行情感分析，从而为市场情绪与股票价格行为之间的动态关系提供新的见解。本研究通过推进互补情感分析工具的整合以及针对不同市场阶段的评估，为将情感分析应用于金融预测的现有...。研究方法：机器学习、情绪分析。

## 10. Long-Term Quantile Treatment Effects with Combined Experimental and Observational Data
- 来源：arxiv
- 作者：Nan Liu, Yanbo Liu, Yuya Sasaki, Yichong Zhang
- 期刊/来源：arXiv
- 发表日期：2026-11-17
- 引用数：0
- 主题：Economics, Finance
- 链接：[链接](http://arxiv.org/abs/2611.22984v1)

**中文摘要（自动生成）**：【金融经济学】本文研究了在短期实验数据与长期观测数据相结合的情况下，长期分位数处理效应（LTQTEs）的识别、估计与推断问题。在潜在无混杂性的框架下，我们确立了LTQTE曲线的识别方法，并推导出了相应的有效影响函数。基于这些影响函数，我们提出了一种半参数高效估计程序，并开发了一种乘数自助法（multiplier bootstrap method），用于对LTQTE曲线进行统一推断，从而能够在连续的分位数指标范围内获得有效的同时置信区间。。研究方法：实验方法。

## 11. Action-outcome coupling: a pre-investment feasibility audit for offline reinforcement learning in supply chain operations
- 来源：arxiv
- 作者：Tung Dang, The Hung Phung, Son Lam Nguyen, Tu Nguyen
- 期刊/来源：arXiv
- 发表日期：2026-11-17
- 引用数：0
- 主题：Economics, Finance
- 链接：[链接](http://arxiv.org/abs/2611.22921v1)

**中文摘要（自动生成）**：【金融经济学】在物流领域，诸如离线强化学习和次优行动系统之类的规范性分析项目往往在尚未有人验证现有历史数据是否足以支持改进决策策略之前就获得了资金支持。我们通过“行动-结果耦合”这一概念来形式化这种投资前的可行性问题：该指标用于衡量预期结果随记录的行动而发生的变化程度。这种耦合方法为任何策略的可实现价值提供了一个与算法无关的上限，该价值以每次决策的货币单位来表示，适用于单步决策和折现序列决策场景。我们还分析了无效工作流程所带来的渐进性“错误授权”风险，即在同一数据集上拟合价值模型并评估该模型所产生的“贪婪策略”。错误授权率主要受状态单元数量的影响：当状态单元数量从一个时，错误授权率处于较低水平；而当状态单元数量达到几十个时，错误授权率几乎可以确定为必然发生。随后，我们提出了一种审计机制，将历史数据分为四个决策支持层级，分别针对固定策略和上下文相关策略，并提供明确的停止决策的依据。在随机生成的电子商务数据集上，该审计机制推荐了一种固定策略，其带来的收益相当于理论上限的30%；剩余的收益差距反映了在包含80个行动的设计方案下评估结果的不确定性。有两个公共物流数据集在审计过程中未能通过验证：其中一个...。研究方法：随机实验。

## 12. Weighted Proportional Toll Sharing on General Highway Networks
- 来源：arxiv
- 作者：Erfang Shan, Yan Chu
- 期刊/来源：arXiv
- 发表日期：2026-11-17
- 引用数：0
- 主题：Economics, Finance
- 链接：[链接](http://arxiv.org/abs/2611.22892v1)

**中文摘要（自动生成）**：【金融经济学】我们将\citet{wu2024}提出的“路段平等分配（SES）”方法从线性高速公路网络扩展到了包含循环路段的一般高速公路网络。输入数据为外生指定的路线流量分布情况。我们引入了“加权比例分配（WPS）”方法，该方法根据路段的权重长度来分配每条路线的里程收入，并根据路段的附加收费来分配其固定附加费收入。在每个收入组成部分内，采用相同的权重即可恢复路段SES分配结果。我们证明了WPS方法实际上是两种加权Shapley分配方式的叠加，并指出相应的路线博弈模型扩展了线性SES模型中的收益分配与Shapley值表示方法。通过两个公理化特征可以识别WPS方法：第一个特征基于对所有产生正收入的路段实施加法运算及比例分配原则；第二个特征则结合了子高速公路网络的效率评估以及路线取消规则下的加权平均平衡贡献原则。此外，我们还将“路段比例分配”方法扩展到了一般网络环境中，并将其与相应路线博弈的$τ$值等同起来，并通过公理化方法对其分配机制进行了描述。对于“路段补偿分配”模型，我们通过根节点结算处的一致性以及指定根节点随机分配机制下的平均分配规则来描述其分配过程。一个包含循环路段的实例表明，即使起点-终...。
