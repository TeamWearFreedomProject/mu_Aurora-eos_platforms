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

以前の**タイマー診断版**は、UEFI内部に残っていたWatch 3由来の割り込み番号をCP2AのDTBに合わせて修正したものです。[ビルド結果と成果物（Run 36560298201）](https://github.com/TeamWearFreedomProject/mu_Aurora-eos_platforms/actions/runs/36560298201)は成功していますが、実機では暗転と同じWinUSB認識が続きました。成功したビルドは実機での安全性や動作を保証しません。

## リポジトリの見方

- **`Aurora&eos-port`**：Watch 2移植の作業ブランチ。いま読んでいるREADMEはこちらです。
- **`main`**：元のWatch 3向けコードが中心の古いブランチ。現在のデフォルトブランチです。
- [詳しい技術メモ](Platforms/AuroraPkg/README.md)：CP2A画像の解析、メモリマップ、ACPI、未解決点。
- [実機観測の記録](Platforms/AuroraPkg/Research/hardware_observation_2026-09-29_ufp.json)：一時起動とUSB認識。端末固有のシリアル番号は含みません。

## 2026-09-30の診断更新

タイマー診断版でも暗転後に `045E:066B` のWinUSBが認識されました。次の設定画面直行版では青い目印が一瞬出た後に画面が消え、USBも認識されなくなったとの報告があります。設定画面直行版は誤って `boot_b` に永続書き込みされ、その後、所有者が純正bootを戻したと報告しています。

現在の診断版は、設定画面を呼ばず青い目印を一度だけ描いて保持します。[狙いと観測の読み方](Platforms/AuroraPkg/Research/blue_display_hold_diagnostic_2026-09-30.md)を参照してください。成果物名は `aurora-CP2A-blue-hold-diagnostic-UNVERIFIED` です。この版の実機結果は未確認です。

## 次に調べること

1. 実機の現在のファームウェア・スロット・復旧手段を再確認する。
2. 青保持診断版を一時起動し、約60秒の表示とUSB認識を記録する。
3. 青が残るなら設定画面の初期化経路、消えるなら設定画面より前から動く表示・イベント・リセット処理を切り分ける。

## Linuxカーネル起動までの目標

公開を考える最初の節目は、Aurora実機でUEFIからLinuxカーネルに制御が渡り、起動ログで再現を確認できた時点です。現時点ではカーネル起動を確認していません。

1. ロゴ後にどこまで実行されたかを切り分け、UEFIの画面・入力・起動選択を安定させる。
2. 起動経路を決めて、Aurora用のカーネル、デバイスツリー、起動パラメータとログ取得方法を検証する。
3. 一時起動でカーネルの初期ログを確認し、再現条件と復旧手順を文書にする。

現在のFDには `QcomModulePkg/Application/LinuxLoader` が含まれています。ただし、その `LinuxLoader.c` は `BootIntoFastboot = TRUE` に固定されており、通常の `LoadImageAndAuth` / `BootLinux` 経路をそのまま使える状態ではありません。これが実機で選択・実行された証拠もまだありません。Linux向けの起動経路は、UEFI表示の切り分け後に別途確認が必要です。

**成果物は研究・診断用です。永続パーティションへ書き込まないでください。** 現在のコードにはWatch 3由来で未検証の初期化・メモリ利用が残っています。公式の[Pixel Watch 3 UEFIガイド](https://github.com/WOA-Project/PixelWatch-Guides)はこのWatch 2移植の手順ではありません。

## ビルド

GitHub Actionsの[「Aurora UEFI (experimental compile only)」](.github/workflows/aurora-build.yml)が静的チェック、UEFIビルド、イメージ構造検証を実行します。ローカルでUEFIファームウェアボリュームのみを作る場合は、依存環境とサブモジュールを用意して `bash ./build_fd_aurora.sh` を実行します。詳しくは[技術メモ](Platforms/AuroraPkg/README.md)を参照してください。

## 元プロジェクト

[Project Mu](https://microsoft.github.io/mu/)と[WOA-Project/mu_seluna_platforms](https://github.com/WOA-Project/mu_seluna_platforms)のコード・構成を利用しています。各ファイルのライセンスと著作権表記を確認してください。
