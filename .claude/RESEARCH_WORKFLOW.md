# リサーチワークフロー ドキュメント

## 概要
このリポジトリには、AIと人間が協働するリサーチワークフロースキルが含まれています。
粗いテーマ入力から、ChatGPT Deep Research投げ込み用の精密な論点設計書を生成し、
Notionに構造化して保存します。

## 使い方

### 起動
```
/research [テーマや背景を自由に記述]
```

例：
```
/research 国内のCO2回収・輸送・利活用の市場動向と主要プレイヤーを把握したい
/research SaaSスタートアップへの補助金活用可能性を整理したい
/research 農業ロボットの海外展開先候補を調べたい
```

### フロー
1. **論点ヒアリング** — Claudeが3〜5問の質問をしながら論点を精緻化
2. **論点マップ + 仮説構造化** — 問いの体系と仮説リストを生成
3. **初期デスクリサーチ** — 公式・一次情報優先でWeb調査
4. **DeepResearch設計書** — ChatGPT Deep Researchに投げ込めるプロンプトを生成
5. **Notion出力** — Source DB + リサーチドキュメントとして保存

## ファイル構成

```
.claude/
  skills/
    research.md              # メインスキル（ワークフロー制御）
  agents/
    desk-researcher.md       # Web調査専門エージェント
    hypothesis-builder.md    # 論点・仮説構造化エージェント
    notion-writer.md         # Notion出力エージェント
  templates/
    deep-research-brief.md   # DeepResearch設計書テンプレート
  RESEARCH_WORKFLOW.md       # このファイル
```

## 参考

- 設計参考: https://github.com/masaki69/consultingskills_public/
- ワークフロー概念: https://note.com/masakikono/n/n0f7faa03a113
