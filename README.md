# Personal Agent Skills

保存经过实际使用验证的 Agent Skills，用于版本控制和跨电脑、跨 Agent 分发。[本 GitHub 仓库](https://github.com/KevinH7512/Personal-Agent-Skills)是这些 Skills 的 canonical source；修改以仓库版本为准。

## Skills

| Skill | 用途 |
| --- | --- |
| [tutoring-handout-builder](skills/tutoring-handout-builder/SKILL.md) | 从 K/Q/A 素材生成集中式或穿插式学生/答案 Word 讲义，或将化学学习 PDF 重建为可编辑讲义。 |

## 结构

```text
skills/
└── tutoring-handout-builder/
    ├── SKILL.md
    ├── references/
    ├── scripts/
    └── agents/openai.yaml
```

## 下载与使用

```sh
git clone https://github.com/KevinH7512/Personal-Agent-Skills.git
```

也可在 GitHub 页面选择 **Code → Download ZIP** 并解压。

将需要的完整 Skill 文件夹复制到目标 Agent 支持的 Skill 安装位置，保留其相对目录结构，然后按该 Agent 的方式加载或调用。不同 Agent 的安装位置和加载机制可能不同。更新时在仓库中运行 `git pull`，再同步需要的 Skill 文件夹；覆盖安装副本前请保存自己的改动。

当前版本保留了已验证的 Codex/Astra 相关说明及可选界面元数据 `agents/openai.yaml`。原文要求外部 `documents`/`pdf` skills 和宿主自带 Python 运行时，尚待确认最小可移植性调整。校验脚本使用 `python-docx`、`lxml`；文档渲染还需要相应软件和字体，下载仓库不会自动安装这些依赖。

许可证：[MIT](LICENSE)。许可证适用于本仓库内容，不授予输入教材、字体或外部软件的使用与再分发权。
