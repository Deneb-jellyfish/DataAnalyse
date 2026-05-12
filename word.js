const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  HeadingLevel, AlignmentType, BorderStyle, WidthType, ShadingType,
  LevelFormat, PageBreak
} = require('docx');
const fs = require('fs');

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const cellMargins = { top: 100, bottom: 100, left: 150, right: 150 };

function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 320, after: 160 },
    children: [new TextRun({ text, bold: true, size: 32, font: "Arial", color: "1F3864" })]
  });
}
function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 240, after: 120 },
    children: [new TextRun({ text, bold: true, size: 26, font: "Arial", color: "2E75B6" })]
  });
}
function h3(text) {
  return new Paragraph({
    spacing: { before: 200, after: 80 },
    children: [new TextRun({ text, bold: true, size: 24, font: "Arial", color: "375623" })]
  });
}
function p(text, opts = {}) {
  return new Paragraph({
    spacing: { before: 60, after: 100 },
    children: [new TextRun({ text, size: 22, font: "Arial", ...opts })]
  });
}
function bullet(text, bold_prefix = null) {
  const runs = [];
  if (bold_prefix) {
    runs.push(new TextRun({ text: bold_prefix + " ", bold: true, size: 22, font: "Arial" }));
    runs.push(new TextRun({ text, size: 22, font: "Arial" }));
  } else {
    runs.push(new TextRun({ text, size: 22, font: "Arial" }));
  }
  return new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { before: 40, after: 40 }, children: runs });
}
function numbered(text, bold_prefix = null) {
  const runs = [];
  if (bold_prefix) {
    runs.push(new TextRun({ text: bold_prefix + " ", bold: true, size: 22, font: "Arial" }));
    runs.push(new TextRun({ text, size: 22, font: "Arial" }));
  } else {
    runs.push(new TextRun({ text, size: 22, font: "Arial" }));
  }
  return new Paragraph({ numbering: { reference: "numbers", level: 0 }, spacing: { before: 40, after: 40 }, children: runs });
}
function colorBox(text, fill = "EBF3FB") {
  return new Table({
    width: { size: 9360, type: WidthType.DXA }, columnWidths: [9360],
    rows: [new TableRow({ children: [new TableCell({
      borders, width: { size: 9360, type: WidthType.DXA },
      shading: { fill, type: ShadingType.CLEAR }, margins: cellMargins,
      children: [new Paragraph({ spacing: { before: 60, after: 60 }, children: [new TextRun({ text, size: 22, font: "Arial", italics: true })] })]
    })]})]
  });
}
function memberHeader(letter, name, role, fill) {
  return new Table({
    width: { size: 9360, type: WidthType.DXA }, columnWidths: [800, 8560],
    rows: [new TableRow({ children: [
      new TableCell({
        borders, width: { size: 800, type: WidthType.DXA },
        shading: { fill, type: ShadingType.CLEAR }, margins: cellMargins,
        children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: letter, bold: true, size: 36, font: "Arial", color: "FFFFFF" })] })]
      }),
      new TableCell({
        borders, width: { size: 8560, type: WidthType.DXA },
        shading: { fill: "F8F8F8", type: ShadingType.CLEAR }, margins: cellMargins,
        children: [
          new Paragraph({ spacing: { before: 40, after: 20 }, children: [new TextRun({ text: name, bold: true, size: 26, font: "Arial" })] }),
          new Paragraph({ spacing: { before: 0, after: 40 }, children: [new TextRun({ text: role, size: 20, font: "Arial", color: "666666" })] })
        ]
      })
    ]})]
  });
}
function taskTable(rows) {
  const headerRow = new TableRow({
    tableHeader: true,
    children: [
      new TableCell({ borders, width:{size:1200,type:WidthType.DXA}, shading:{fill:"D9E2F3",type:ShadingType.CLEAR}, margins:cellMargins, children:[new Paragraph({children:[new TextRun({text:"时间",bold:true,size:20,font:"Arial"})]})] }),
      new TableCell({ borders, width:{size:2000,type:WidthType.DXA}, shading:{fill:"D9E2F3",type:ShadingType.CLEAR}, margins:cellMargins, children:[new Paragraph({children:[new TextRun({text:"任务",bold:true,size:20,font:"Arial"})]})] }),
      new TableCell({ borders, width:{size:4560,type:WidthType.DXA}, shading:{fill:"D9E2F3",type:ShadingType.CLEAR}, margins:cellMargins, children:[new Paragraph({children:[new TextRun({text:"具体做什么",bold:true,size:20,font:"Arial"})]})] }),
      new TableCell({ borders, width:{size:1600,type:WidthType.DXA}, shading:{fill:"D9E2F3",type:ShadingType.CLEAR}, margins:cellMargins, children:[new Paragraph({children:[new TextRun({text:"交付物",bold:true,size:20,font:"Arial"})]})] }),
    ]
  });
  const dataRows = rows.map((r, i) => new TableRow({ children: [
    new TableCell({ borders, width:{size:1200,type:WidthType.DXA}, shading:{fill:i%2===0?"FFFFFF":"F5F8FF",type:ShadingType.CLEAR}, margins:cellMargins, children:[new Paragraph({children:[new TextRun({text:r.day,size:20,font:"Arial",bold:true})]})] }),
    new TableCell({ borders, width:{size:2000,type:WidthType.DXA}, shading:{fill:i%2===0?"FFFFFF":"F5F8FF",type:ShadingType.CLEAR}, margins:cellMargins, children:[new Paragraph({children:[new TextRun({text:r.title,size:20,font:"Arial",bold:true})]})] }),
    new TableCell({ borders, width:{size:4560,type:WidthType.DXA}, shading:{fill:i%2===0?"FFFFFF":"F5F8FF",type:ShadingType.CLEAR}, margins:cellMargins, children:[new Paragraph({children:[new TextRun({text:r.detail,size:20,font:"Arial"})]})] }),
    new TableCell({ borders, width:{size:1600,type:WidthType.DXA}, shading:{fill:i%2===0?"FFFFFF":"F5F8FF",type:ShadingType.CLEAR}, margins:cellMargins, children:[new Paragraph({children:[new TextRun({text:r.deliver,size:20,font:"Arial",color:"1D6F42"})]})] }),
  ]}));
  return new Table({ width:{size:9360,type:WidthType.DXA}, columnWidths:[1200,2000,4560,1600], rows:[headerRow,...dataRows] });
}
function sp(before=120, after=60) {
  return new Paragraph({ spacing: { before, after }, children: [] });
}
function pageBreak() {
  return new Paragraph({ children: [new PageBreak()] });
}

// ── 分工卡片式布局（仿截图样式） ──
function roleCard(dayLabel, title, detail, deliver, deliverColor, bg) {
  // detail可以是字符串或字符串数组
  const detailLines = Array.isArray(detail) ? detail : [detail];
  const children = [
    new Paragraph({ spacing:{before:60,after:80}, children:[new TextRun({text:dayLabel, size:18, font:"Arial", color:"888888"})] }),
    new Paragraph({ spacing:{before:0,after:100}, children:[new TextRun({text:title, bold:true, size:24, font:"Arial"})] }),
    ...detailLines.map(line => new Paragraph({ spacing:{before:20,after:20}, children:[new TextRun({text:line, size:20, font:"Arial"})] })),
    sp(80,40),
    new Paragraph({ spacing:{before:40,after:60}, children:[new TextRun({text:"交付：" + deliver, size:19, font:"Arial", color: deliverColor, bold:true})] }),
  ];
  return new TableCell({
    borders, width:{size:4680,type:WidthType.DXA},
    shading:{fill:bg,type:ShadingType.CLEAR}, margins:{top:160,bottom:160,left:200,right:200},
    children
  });
}

function roleCardFull(dayLabel, title, detail, deliver, deliverColor, bg) {
  const detailLines = Array.isArray(detail) ? detail : [detail];
  const children = [
    new Paragraph({ spacing:{before:60,after:80}, children:[new TextRun({text:dayLabel, size:18, font:"Arial", color:"888888"})] }),
    new Paragraph({ spacing:{before:0,after:100}, children:[new TextRun({text:title, bold:true, size:24, font:"Arial"})] }),
    ...detailLines.map(line => new Paragraph({ spacing:{before:20,after:20}, children:[new TextRun({text:line, size:20, font:"Arial"})] })),
    sp(80,40),
    new Paragraph({ spacing:{before:40,after:60}, children:[new TextRun({text:"交付：" + deliver, size:19, font:"Arial", color: deliverColor, bold:true})] }),
  ];
  return new TableCell({
    borders, width:{size:9360,type:WidthType.DXA},
    shading:{fill:bg,type:ShadingType.CLEAR}, margins:{top:160,bottom:160,left:200,right:200},
    children
  });
}

function twoColRow(left, right) {
  return new TableRow({ children:[left, right] });
}
function oneColRow(cell) {
  return new TableRow({ children:[cell] });
}
function cardTable(rows) {
  return new Table({ width:{size:9360,type:WidthType.DXA}, columnWidths:[4680,4680], rows });
}
function cardTableFull(rows) {
  return new Table({ width:{size:9360,type:WidthType.DXA}, columnWidths:[9360], rows });
}

// member section header (仿截图)
function memberCardHeader(letter, name, role, avatarFill) {
  return new Table({
    width:{size:9360,type:WidthType.DXA}, columnWidths:[700,8660],
    rows:[new TableRow({children:[
      new TableCell({
        borders, width:{size:700,type:WidthType.DXA},
        shading:{fill:avatarFill,type:ShadingType.CLEAR}, margins:cellMargins,
        children:[new Paragraph({alignment:AlignmentType.CENTER, children:[new TextRun({text:letter,bold:true,size:32,font:"Arial",color:"FFFFFF"})]})]
      }),
      new TableCell({
        borders, width:{size:8660,type:WidthType.DXA},
        shading:{fill:"F5F5F5",type:ShadingType.CLEAR}, margins:{top:80,bottom:80,left:180,right:120},
        children:[
          new Paragraph({spacing:{before:30,after:20}, children:[new TextRun({text:name,bold:true,size:26,font:"Arial"})]}),
          new Paragraph({spacing:{before:0,after:30}, children:[new TextRun({text:"负责："+role,size:19,font:"Arial",color:"777777"})]}),
        ]
      })
    ]})]
  });
}

const doc = new Document({
  numbering: {
    config: [
      { reference:"bullets", levels:[{level:0,format:LevelFormat.BULLET,text:"\u2022",alignment:AlignmentType.LEFT,style:{paragraph:{indent:{left:720,hanging:360}}}}] },
      { reference:"numbers", levels:[{level:0,format:LevelFormat.DECIMAL,text:"%1.",alignment:AlignmentType.LEFT,style:{paragraph:{indent:{left:720,hanging:360}}}}] },
    ]
  },
  styles: {
    default:{ document:{ run:{ font:"Arial", size:22 } } },
    paragraphStyles:[
      {id:"Heading1",name:"Heading 1",basedOn:"Normal",next:"Normal",quickFormat:true,run:{size:32,bold:true,font:"Arial"},paragraph:{spacing:{before:320,after:160},outlineLevel:0}},
      {id:"Heading2",name:"Heading 2",basedOn:"Normal",next:"Normal",quickFormat:true,run:{size:26,bold:true,font:"Arial"},paragraph:{spacing:{before:240,after:120},outlineLevel:1}},
    ]
  },
  sections:[{
    properties:{
      page:{ size:{width:11906,height:16838}, margin:{top:1440,right:1440,bottom:1440,left:1440} }
    },
    children:[

      // ── 封面 ──
      sp(600),
      new Paragraph({alignment:AlignmentType.CENTER,spacing:{before:0,after:180},children:[new TextRun({text:"SSE 2026 数据分析与挖掘",size:24,font:"Arial",color:"888888"})]}),
      new Paragraph({alignment:AlignmentType.CENTER,spacing:{before:0,after:140},children:[new TextRun({text:"项目说明书",size:52,bold:true,font:"Arial",color:"1F3864"})]}),
      new Paragraph({alignment:AlignmentType.CENTER,spacing:{before:0,after:100},children:[new TextRun({text:"基于图神经网络与聚类分析的分子性质预测",size:34,font:"Arial",color:"2E75B6"})]}),
      sp(160),
      colorBox("本文档面向所有组员，无论是否有机器学习背景，读完后都应能理解：我们在做什么、为什么这样做、自己负责哪部分、以及怎么做。", "EBF3FB"),
      sp(500),
      new Paragraph({alignment:AlignmentType.CENTER,children:[new TextRun({text:"截止日期：2026年5月20日",size:24,font:"Arial",color:"C00000",bold:true})]}),
      sp(200),
      pageBreak(),

      // ── 第一章 ──
      h1("第一章  我们在做什么"),
      h2("1.1  用一句话说"),
      colorBox("训练一个AI模型，给它一个分子的原子结构，它能预测这个分子的物理性质（偶极矩）。同时用聚类方法分析分子的自然分组规律。速度比传统计算快100万倍，精度损失不到5%。", "FFF2CC"),
      sp(),
      h2("1.2  为什么要做这件事"),
      p("预测分子的物理性质在药物研发、材料科学里非常重要。传统做法是用量子力学公式（DFT）精确计算，问题是："),
      bullet("算一个小分子需要几分钟到几小时"),
      bullet("算一个中等分子需要几天"),
      bullet("候选药物分子有10亿个，全部算完需要100万年"),
      sp(),
      p("AI的方案：先用DFT算好13万个分子的性质存进数据库（这就是QM9数据集），再用这些数据训练神经网络，让它学会\"看分子结构猜性质\"的规律。"),
      colorBox("AI不是替代精确计算，而是当粗筛器，让精确计算只用在刀刃上。这就是AI4S（AI for Science）的核心价值。", "E2EFDA"),
      sp(),
      h2("1.3  和\"数据挖掘\"课的关系"),
      p("这个课叫数据分析与挖掘，我们的项目完全符合这个主题："),
      bullet("真实数据集：QM9，13万条分子数据"),
      bullet("数据探索分析：分布图、相关性分析，发现数据规律"),
      bullet("聚类分析：用KMeans对分子分组，看不同类型分子的性质差异（课上学的核心内容）"),
      bullet("特征工程：怎么把分子转成数字，加入物理先验知识"),
      bullet("多模型对比：随机森林 vs 图神经网络，消融实验"),
      sp(200),
      pageBreak(),

      // ── 第二章 ──
      h1("第二章  数据集介绍——QM9是什么"),
      p("QM9是一个公开的分子数据集，包含133,885个小分子（每个最多29个原子，只含H、C、N、O、F五种元素）。每条数据包含两部分："),
      sp(),
      new Table({
        width:{size:9360,type:WidthType.DXA}, columnWidths:[2000,3680,3680],
        rows:[
          new TableRow({children:[
            new TableCell({borders,width:{size:2000,type:WidthType.DXA},shading:{fill:"D9E2F3",type:ShadingType.CLEAR},margins:cellMargins,children:[new Paragraph({children:[new TextRun({text:"部分",bold:true,size:20,font:"Arial"})]})] }),
            new TableCell({borders,width:{size:3680,type:WidthType.DXA},shading:{fill:"D9E2F3",type:ShadingType.CLEAR},margins:cellMargins,children:[new Paragraph({children:[new TextRun({text:"内容",bold:true,size:20,font:"Arial"})]})] }),
            new TableCell({borders,width:{size:3680,type:WidthType.DXA},shading:{fill:"D9E2F3",type:ShadingType.CLEAR},margins:cellMargins,children:[new Paragraph({children:[new TextRun({text:"在项目里的作用",bold:true,size:20,font:"Arial"})]})] }),
          ]}),
          new TableRow({children:[
            new TableCell({borders,width:{size:2000,type:WidthType.DXA},margins:cellMargins,children:[new Paragraph({children:[new TextRun({text:"分子结构（输入）",size:20,font:"Arial"})]})] }),
            new TableCell({borders,width:{size:3680,type:WidthType.DXA},margins:cellMargins,children:[new Paragraph({children:[new TextRun({text:"原子列表（C/H/N/O/F）+ 化学键列表",size:20,font:"Arial"})]})] }),
            new TableCell({borders,width:{size:3680,type:WidthType.DXA},margins:cellMargins,children:[new Paragraph({children:[new TextRun({text:"喂给AI模型的输入",size:20,font:"Arial"})]})] }),
          ]}),
          new TableRow({children:[
            new TableCell({borders,width:{size:2000,type:WidthType.DXA},shading:{fill:"F5F8FF",type:ShadingType.CLEAR},margins:cellMargins,children:[new Paragraph({children:[new TextRun({text:"19个物理性质（标签）",size:20,font:"Arial"})]})] }),
            new TableCell({borders,width:{size:3680,type:WidthType.DXA},shading:{fill:"F5F8FF",type:ShadingType.CLEAR},margins:cellMargins,children:[new Paragraph({children:[new TextRun({text:"偶极矩、能量、HOMO能级、极化率…等",size:20,font:"Arial"})]})] }),
            new TableCell({borders,width:{size:3680,type:WidthType.DXA},shading:{fill:"F5F8FF",type:ShadingType.CLEAR},margins:cellMargins,children:[new Paragraph({children:[new TextRun({text:"我们预测偶极矩这1个目标",size:20,font:"Arial"})]})] }),
          ]}),
        ]
      }),
      sp(),
      p("偶极矩是衡量分子\"电荷分布是否均匀\"的数值，单位Debye（D）。偶极矩越大分子越容易溶于水，是药物研发的重要筛选指标。"),
      sp(200),
      pageBreak(),

      // ── 第三章 ──
      h1("第三章  项目完整流程"),
      h2("第一步：数据下载与环境搭建（成员A，Day 1）"),
      p("用一行Python代码下载QM9数据集（约30MB），安装所需库。必须今天完成，后面所有人都依赖这一步。"),
      sp(),
      h2("第二步：数据探索分析（成员A，Day 2~3）"),
      p("在训练模型之前先\"认识\"这份数据，具体画六张图："),
      bullet("分子大小分布图：看大多数分子有几个原子，有没有异常值"),
      bullet("偶极矩分布图：看预测目标的范围和分布，决定要不要做数据预处理"),
      bullet("原子类型占比图：H和C最多，F很少——AI对稀少类型预测较差，报告里要说明"),
      bullet("性质相关性热力图：看19个性质之间有什么规律"),
      bullet("KMeans聚类图（新）：把13万个分子分成5组，用PCA降维后可视化，看分子有无自然分组"),
      bullet("各簇偶极矩箱线图（新）：比较每组分子的偶极矩分布，验证聚类是否有实际意义"),
      sp(),
      colorBox("前四张图是常规数据探索；后两张是课上学的聚类分析，直接体现\"数据挖掘\"课程主题，是报告数据分析章节的亮点。", "FFF2CC"),
      sp(),

      h2("第三步：特征工程（成员A+B，Day 3~4）"),
      h3("方法一：分子指纹（给随机森林和聚类用）"),
      p("把分子压缩成2048位的0/1数组，每一位代表\"有没有某种结构特征\"。简单但丢失了原子间的空间关系。"),
      h3("方法二：图结构表示（给GNN用）"),
      p("把分子看成图：原子=节点，化学键=边。每个原子有一个特征向量（身份证）。"),
      p("默认11维：原子序数、电荷、是否在环里等基本信息。"),
      p("加入物理特征后14维，额外记录："),
      bullet("电负性：O=3.44，C=2.55，H=2.20。电负性差异大的原子连在一起偶极矩就大——物理规律"),
      bullet("杂化方式（sp/sp2/sp3）：决定分子空间形状"),
      bullet("是否在芳香环中：苯环类分子性质与普通分子有系统差异"),
      sp(),
      colorBox("加入物理特征就是把化学知识\"告诉\"模型，这是报告里\"物理先验提升AI性能\"论点的核心实验证据。", "E2EFDA"),
      sp(),

      h2("第四步：训练三个模型做消融实验（成员B+C，Day 3~5）"),
      p("消融实验：每次去掉一个东西，看效果掉了多少，证明每个组件都有用。"),
      sp(),
      new Table({
        width:{size:9360,type:WidthType.DXA}, columnWidths:[600,2200,2560,1600,2400],
        rows:[
          new TableRow({children:[
            new TableCell({borders,width:{size:600,type:WidthType.DXA},shading:{fill:"D9E2F3",type:ShadingType.CLEAR},margins:cellMargins,children:[new Paragraph({children:[new TextRun({text:"编号",bold:true,size:20,font:"Arial"})]})] }),
            new TableCell({borders,width:{size:2200,type:WidthType.DXA},shading:{fill:"D9E2F3",type:ShadingType.CLEAR},margins:cellMargins,children:[new Paragraph({children:[new TextRun({text:"模型",bold:true,size:20,font:"Arial"})]})] }),
            new TableCell({borders,width:{size:2560,type:WidthType.DXA},shading:{fill:"D9E2F3",type:ShadingType.CLEAR},margins:cellMargins,children:[new Paragraph({children:[new TextRun({text:"输入特征",bold:true,size:20,font:"Arial"})]})] }),
            new TableCell({borders,width:{size:1600,type:WidthType.DXA},shading:{fill:"D9E2F3",type:ShadingType.CLEAR},margins:cellMargins,children:[new Paragraph({children:[new TextRun({text:"预期效果",bold:true,size:20,font:"Arial"})]})] }),
            new TableCell({borders,width:{size:2400,type:WidthType.DXA},shading:{fill:"D9E2F3",type:ShadingType.CLEAR},margins:cellMargins,children:[new Paragraph({children:[new TextRun({text:"证明什么",bold:true,size:20,font:"Arial"})]})] }),
          ]}),
          new TableRow({children:[
            new TableCell({borders,width:{size:600,type:WidthType.DXA},margins:cellMargins,children:[new Paragraph({children:[new TextRun({text:"Exp-1",size:20,font:"Arial"})]})] }),
            new TableCell({borders,width:{size:2200,type:WidthType.DXA},margins:cellMargins,children:[new Paragraph({children:[new TextRun({text:"随机森林",size:20,font:"Arial"})]})] }),
            new TableCell({borders,width:{size:2560,type:WidthType.DXA},margins:cellMargins,children:[new Paragraph({children:[new TextRun({text:"分子指纹（丢失结构）",size:20,font:"Arial"})]})] }),
            new TableCell({borders,width:{size:1600,type:WidthType.DXA},margins:cellMargins,children:[new Paragraph({children:[new TextRun({text:"最差（基准）",size:20,font:"Arial",color:"C00000"})]})] }),
            new TableCell({borders,width:{size:2400,type:WidthType.DXA},margins:cellMargins,children:[new Paragraph({children:[new TextRun({text:"GNN优于传统ML",size:20,font:"Arial"})]})] }),
          ]}),
          new TableRow({children:[
            new TableCell({borders,width:{size:600,type:WidthType.DXA},shading:{fill:"F5F8FF",type:ShadingType.CLEAR},margins:cellMargins,children:[new Paragraph({children:[new TextRun({text:"Exp-2",size:20,font:"Arial"})]})] }),
            new TableCell({borders,width:{size:2200,type:WidthType.DXA},shading:{fill:"F5F8FF",type:ShadingType.CLEAR},margins:cellMargins,children:[new Paragraph({children:[new TextRun({text:"基础GNN",size:20,font:"Arial"})]})] }),
            new TableCell({borders,width:{size:2560,type:WidthType.DXA},shading:{fill:"F5F8FF",type:ShadingType.CLEAR},margins:cellMargins,children:[new Paragraph({children:[new TextRun({text:"原子图，基础11维特征",size:20,font:"Arial"})]})] }),
            new TableCell({borders,width:{size:1600,type:WidthType.DXA},shading:{fill:"F5F8FF",type:ShadingType.CLEAR},margins:cellMargins,children:[new Paragraph({children:[new TextRun({text:"中等",size:20,font:"Arial",color:"7F6000"})]})] }),
            new TableCell({borders,width:{size:2400,type:WidthType.DXA},shading:{fill:"F5F8FF",type:ShadingType.CLEAR},margins:cellMargins,children:[new Paragraph({children:[new TextRun({text:"保留结构有帮助",size:20,font:"Arial"})]})] }),
          ]}),
          new TableRow({children:[
            new TableCell({borders,width:{size:600,type:WidthType.DXA},margins:cellMargins,children:[new Paragraph({children:[new TextRun({text:"Exp-3",size:20,font:"Arial"})]})] }),
            new TableCell({borders,width:{size:2200,type:WidthType.DXA},margins:cellMargins,children:[new Paragraph({children:[new TextRun({text:"GNN + 物理特征",bold:true,size:20,font:"Arial"})]})] }),
            new TableCell({borders,width:{size:2560,type:WidthType.DXA},margins:cellMargins,children:[new Paragraph({children:[new TextRun({text:"原子图 + 电负性/杂化/芳香性",size:20,font:"Arial"})]})] }),
            new TableCell({borders,width:{size:1600,type:WidthType.DXA},margins:cellMargins,children:[new Paragraph({children:[new TextRun({text:"最好",bold:true,size:20,font:"Arial",color:"1D6F42"})]})] }),
            new TableCell({borders,width:{size:2400,type:WidthType.DXA},margins:cellMargins,children:[new Paragraph({children:[new TextRun({text:"物理先验提升精度",size:20,font:"Arial"})]})] }),
          ]}),
        ]
      }),
      sp(),

      h2("第五步：聚类深入分析（成员C，Day 5）"),
      p("聚类不只是画个图，还要做进一步分析，让它在报告里有实质内容："),
      bullet("分析每个簇内模型的预测误差：哪类分子预测好，哪类预测差"),
      bullet("找出预测差的原因：通常是含F原子的分子，因为数据集里F原子太少，AI学得不够"),
      bullet("结论写法：\"含F原子的簇（Cluster X）误差比其他簇高Y倍，说明数据不均衡是主要瓶颈\""),
      colorBox("这个分析直接呼应\"数据质量影响AI性能\"的核心论点，是整个报告逻辑闭环的关键一步。", "FFF2CC"),
      sp(),

      h2("第六步：结果图表与报告（成员C+D，Day 6~8）"),
      p("成员C画5张结果图，成员D整合进报告，写成10页以内："),
      numbered("Abstract：三句话概括问题/方法/结论"),
      numbered("Introduction：为什么用AI预测分子性质"),
      numbered("Related Work：QM9数据集介绍、GNN发展"),
      numbered("Data Analysis：6张探索图（含KMeans聚类图）+ 分析文字"),
      numbered("Methodology：三种模型的原理和区别"),
      numbered("Experiments：消融实验 + 聚类误差分析"),
      numbered("Conclusion：总结核心论点"),

      sp(200),
      pageBreak(),

      // ── 第四章：分工 ──
      h1("第四章  四人详细分工"),
      sp(80),

      // ── 成员A ──
      memberCardHeader("A", "成员A　数据工程师", "数据下载 · 探索分析 · KMeans聚类 · 可视化 · 分子Demo图", "2E75B6"),
      sp(80),
      cardTable([
        twoColRow(
          roleCard("Day 1 · 5/12", "环境搭建 + 数据下载",
            ["安装所有依赖库：", "torch-geometric, rdkit, matplotlib,", "seaborn, scikit-learn", "下载QM9数据集，确认能读出", "一条数据不报错"],
            "环境跑通截图", "1D6F42", "FFFFFF"),
          roleCard("Day 2 · 5/13", "数据探索分析",
            ["画4张基础图：", "· 分子原子数量分布柱状图", "· 偶极矩分布直方图", "· 原子类型占比饼图", "· 19个性质相关性热力图", "每张图附2-3句话说明发现了什么"],
            "4张PNG图", "1D6F42", "F8FBFF")
        ),
        twoColRow(
          roleCard("Day 3 · 5/14", "KMeans聚类分析（新）",
            ["对分子指纹做KMeans（k=5）", "用PCA降到2维后可视化，", "画聚类散点图", "再画各簇偶极矩箱线图", "分析：不同簇的偶极矩是否", "有明显差异？"],
            "2张聚类PNG图", "1D6F42", "FFFFFF"),
          roleCard("Day 3 · 5/14", "提取分子指纹",
            ["用RDKit把每个分子转成", "2048维Morgan指纹，", "生成X_train和X_test的", "numpy数组文件，", "传给成员C用于随机森林", "和聚类"],
            "fingerprints.py + .npy文件", "1D6F42", "F8FBFF")
        ),
        twoColRow(
          roleCard("Day 6 · 5/17", "分子可视化Demo",
            ["用RDKit画10个分子结构图，", "标注真实偶极矩和预测值。", "挑预测准和预测差的各几个", "做对比，分析误差原因", "（通常是含F的稀少分子）"],
            "demo_mols.png", "1D6F42", "FFFFFF"),
          new TableCell({borders, width:{size:4680,type:WidthType.DXA}, shading:{fill:"F5F5F5",type:ShadingType.CLEAR}, margins:cellMargins, children:[new Paragraph({children:[]})]})
        ),
      ]),
      sp(200),

      // ── 成员B ──
      memberCardHeader("B", "成员B　模型工程师", "GNN模型实现 · 训练脚本 · 加入物理特征", "375623"),
      sp(80),
      cardTable([
        twoColRow(
          roleCard("Day 2 · 5/13", "GNN骨架",
            ["实现MolGNN类：", "· 3层GCNConv（图卷积层）", "· global_mean_pool", "  （所有原子特征取平均）", "· 全连接层输出偶极矩", "跑通前向传播不报错即可"],
            "model.py", "3C3489", "FFFFFF"),
          roleCard("Day 3~4 · 5/14-15", "完整训练循环",
            ["写训练脚本：DataLoader、", "训练循环（50个epoch）、", "验证集loss记录、保存权重。", "用MSE损失 + Adam优化器，", "学习率0.001"],
            "train.py + gnn_base.pt", "3C3489", "F8F8FF")
        ),
        twoColRow(
          roleCard("Day 5 · 5/16", "加入物理特征",
            ["用RDKit给每个原子额外提取：", "· 电负性（按原子类型查表）", "· 杂化方式（sp=0/sp2=1/sp3=2）", "· 是否在芳香环（0或1）", "原11维→新14维，重新训练"],
            "train_physics.py + gnn_physics.pt", "3C3489", "FFFFFF"),
          roleCard("Day 6 · 5/17", "输出预测结果",
            ["用两个模型跑测试集，", "把预测值和真实值存成CSV，", "传给成员C画散点图", "和计算RMSE/MAE指标"],
            "predictions.csv", "3C3489", "F8F8FF")
        ),
      ]),
      sp(200),

      // ── 成员C ──
      memberCardHeader("C", "成员C　实验分析师", "Baseline模型 · 消融实验 · 聚类深入分析 · 结果图表", "7B3F00"),
      sp(80),
      cardTable([
        twoColRow(
          roleCard("Day 3 · 5/14", "随机森林 Baseline",
            ["拿成员A的分子指纹数组，", "训练随机森林（100棵树），", "记录RMSE和MAE。", "这是消融实验Exp-1，", "预期效果最差，作为基准线"],
            "Exp-1的RMSE/MAE数值", "633806", "FFFFFF"),
          roleCard("Day 4~5 · 5/15-16", "GNN对比实验",
            ["跑完三组对比并记录结果：", "· Exp1：随机森林（成员A指纹）", "· Exp2：基础GNN（gnn_base.pt）", "· Exp3：物理特征GNN", "         （gnn_physics.pt）"],
            "三组实验结果表格", "633806", "F8F8FF")
        ),
        twoColRow(
          roleCard("Day 5 · 5/16", "聚类深入分析（新）",
            ["拿成员A的聚类标签，", "在每个簇内单独评估模型误差：", "哪个簇预测好？哪个差？", "找出原因（含F原子簇误差大）", "结论：数据不均衡是瓶颈"],
            "聚类误差分析表 + 文字说明", "633806", "FFFFFF"),
          roleCard("Day 6 · 5/17", "画结果图表",
            ["画5张图直接放报告：", "· 三组RMSE对比柱状图", "· 最佳模型预测vs真实散点图", "· 训练过程loss曲线", "· 各簇预测误差对比图（新）"],
            "5张结果PNG图", "633806", "F8F8FF")
        ),
      ]),
      sp(200),

      // ── 成员D ──
      memberCardHeader("D", "成员D　报告负责人", "报告撰写 · PPT制作 · 整合全组材料", "7030A0"),
      sp(80),
      cardTable([
        twoColRow(
          roleCard("Day 2~3 · 5/13-14", "报告前半部分",
            ["写Abstract、Introduction、", "Related Work初稿。", "核心论点：DFT精确但慢，", "AI快但需要数据+物理先验，", "聚类揭示数据内在规律"],
            "report_v1.docx（前3节）", "712B13", "FFFFFF"),
          roleCard("Day 5 · 5/16", "报告中间部分",
            ["整合成员A的6张图，", "写Data Analysis章节", "（含KMeans聚类分析内容）。", "画GNN架构示意图，", "写Methodology章节"],
            "report_v2.docx（补4-5节）", "712B13", "F8F8FF")
        ),
        twoColRow(
          roleCard("Day 7 · 5/18", "报告完整版 + PPT",
            ["整合成员C的所有图表，", "写Experiments和Conclusion。", "报告控制在10页以内。", "PPT初稿：8页以内", "（加入聚类分析这一页）"],
            "report_final.pdf + slides.pptx", "712B13", "FFFFFF"),
          roleCard("Day 8 · 5/19", "定稿 + 彩排",
            ["根据全组反馈修改，", "组织演讲彩排，", "分配每人讲哪几页，", "控制在5分钟内，", "准备答辩可能被问的问题"],
            "最终提交版本", "712B13", "F8F8FF")
        ),
      ]),

      sp(200),
      pageBreak(),

      // ── 第五章 ──
      h1("第五章  重要注意事项"),
      h2("5.1  任务依赖关系"),
      bullet("成员A在Day 3必须把分子指纹文件和聚类标签发给成员C，否则C无法开始"),
      bullet("成员B在Day 6必须把predictions.csv发给成员C，否则C无法画散点图"),
      bullet("成员A和C在Day 6晚上必须把所有图发给成员D，否则D无法写Experiments章节"),
      bullet("建议统一用GitHub共享代码和数据，不要用微信传文件"),
      sp(),
      h2("5.2  最容易卡壳的地方"),
      bullet("成员B安装PyTorch Geometric版本冲突——建议Day 1就装好，装不上立刻在群里说"),
      bullet("成员A下载QM9网络问题——如果失败可以从Kaggle手动下载"),
      bullet("成员B训练时loss不下降——通常是学习率问题，换成0.0001试试"),
      bullet("KMeans结果解读——如果5个簇差别不大，换成k=8或k=10再试"),
      sp(),
      h2("5.3  演讲要点（5分钟分配）"),
      bullet("0-1分钟：问题背景，为什么用AI预测分子性质"),
      bullet("1-2分钟：数据分析，包括KMeans聚类发现了什么规律"),
      bullet("2-4分钟：三种模型对比，实验结果，聚类误差分析"),
      bullet("4-5分钟：Demo展示（几个分子的预测图）+ 总结核心论点"),
      sp(),
      colorBox("核心论点（演讲时明确说出）：传统ML丢失分子结构导致误差大；GNN保留结构后误差下降X%；加入物理特征后再下降Y%；聚类分析揭示含F分子是数据不均衡的瓶颈。数据质量、特征设计、模型选择三者缺一不可。", "FFF2CC"),
      sp(400),
      new Paragraph({alignment:AlignmentType.CENTER,children:[new TextRun({text:"祝大家顺利完成项目！",size:24,font:"Arial",color:"888888",italics:true})]}),
    ]
  }]
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync('./项目说明书_分子性质预测_v2.docx', buf);
  console.log('Done');
});