# Pixel Watch 2 (Aurora) UEFI port

> ⭐︎ このプロジェクトは個人が **ChatGPTと協力して** 学習・実験として進めています。解析、コード、文書にもAIの支援を使っています。まだ開発途中なので、完成版の配布や個別サポートは約束できません。

Pixel Watch 2 Wi-Fi（コードネーム **aurora**）向けの、実験中のUEFI移植プロジェクトです。Pixel Watch 3向け[WOA-Project/mu_seluna_platforms](https://github.com/WOA-Project/mu_seluna_platforms)を基にしています。**Windowsの起動や安定したUEFIメニュー表示は、まだ確認できていません。**

> **現在の対象:** CP2A.260603.001.S1。実機はこの版に戻したとの報告がありますが、セットアップ後のADBによるビルド番号の再確認は未実施です。Pixel Watch 3用の手順・バイナリをPixel Watch 2にそのまま適用しないでください。

## いまどこまで進んだ？

| 項目 | 状態 |
| --- | --- |
| Aurora専用UEFIのコンパイル | GitHub Actionsで成功 |
| CP2A由来のメモリ配置・CPU・タイマー・一部ACPI | 静的解析とCIで検査 |
| 実機への一時起動 | 以前の候補２種類がfastbootに受理された |
| 実機の表示 | ロゴが一瞬見えた後、黒画面。UEFIメニューは未確認 |
| USB | 暗転後、Windowsで `045E:066B` のWinUSB/UFPらしい機器として認識 |
| Mass Storage / Windows起動 | 未確認 |

最新の**タイマー診断版**は、UEFI内部に残っていたWatch 3由来の割り込み番号をCP2AのDTBに合わせて修正したものです。[ビルド結果と成果物（Run 36560298201）](https://github.com/TeamWearFreedomProject/mu_Aurora-eos_platforms/actions/runs/36560298201)は成功していますが、**診断版の実機動作は未確認**です。成功したビルドは実機での安全性や動作を保証しません。

## リポジトリの見方

- **`Aurora&eos-port`**：Watch 2移植の作業ブランチ。いま読んでいるREADMEはこちらです。
- **`main`**：元のWatch 3向けコードが中心の古いブランチ。現在のデフォルトブランチです。
- [詳しい技術メモ](Platforms/AuroraPkg/README.md)：CP2A画像の解析、メモリマップ、ACPI、未解決点。
- [実機観測の記録](Platforms/AuroraPkg/Research/hardware_observation_2026-09-29_ufp.json)：一時起動とUSB認識。端末固有のシリアル番号は含みません。

## 次に調べること

1. 実機の現在のファームウェア・スロット・復旧手段を再確認する。
2. タイマー診断版と以前の候補で、ロゴ後の表示とUSB認識の違いを比較する。
3. 変化がなければ、Watch 3由来の画面・ボタン・ブートメニュー処理を切り分ける。

**成果物は研究・診断用です。永続パーティションへ書き込まないでください。** 現在のコードにはWatch 3由来で未検証の初期化・メモリ利用が残っています。公式の[Pixel Watch 3 UEFIガイド](https://github.com/WOA-Project/PixelWatch-Guides)はこのWatch 2移植の手順ではありません。

## ビルド

GitHub Actionsの[「Aurora UEFI (experimental compile only)」](.github/workflows/aurora-build.yml)が静的チェック、UEFIビルド、イメージ構造検証を実行します。ローカルでUEFIファームウェアボリュームのみを作る場合は、依存環境とサブモジュールを用意して `bash ./build_fd_aurora.sh` を実行します。詳しくは[技術メモ](Platforms/AuroraPkg/README.md)を参照してください。

## 元プロジェクト

[Project Mu](https://microsoft.github.io/mu/)と[WOA-Project/mu_seluna_platforms](https://github.com/WOA-Project/mu_seluna_platforms)のコード・構成を利用しています。各ファイルのライセンスと著作権表記を確認してください。
