# Pixel Watch 2 (Aurora) UEFI port

> ⭐︎ このプロジェクトは個人が **ChatGPTと協力して** 学習・実験として進めています。解析、コード、文書にもAIの支援を使っています。まだ開発途中なので、完成版の配布や個別サポートは約束できません。

Pixel Watch 2 Wi-Fi（コードネーム **aurora**）向けの、実験中のUEFI移植プロジェクトです。Pixel Watch 3向け[WOA-Project/mu_seluna_platforms](https://github.com/WOA-Project/mu_seluna_platforms)を基にしています。**Windowsの起動や安定したUEFIメニュー表示は、まだ確認できていません。**

> **現在の対象:** CP2A.260603.001.S1。実機はこの版に戻したとの報告がありますが、セットアップ後のADBによるビルド番号の再確認は未実施です。Pixel Watch 3用の手順・バイナリをPixel Watch 2にそのまま適用しないでください。

## いまどこまで進んだ？

| 項目 | 状態 |
| --- | --- |
| Aurora専用UEFIのコンパイル | GitHub Actionsで成功 |
| CP2A由来のメモリ配置・CPU・タイマー・一部ACPI | 静的解析とCIで検査 |
| 実機への一時起動 | 複数の候補が受理された。一時的なLoad Errorの原因は未確定 |
| 実機の表示 | 最新の数値診断で上段132・下段62が残ったとの報告。メニューは未確認 |
| USB | 以前の版では `045E:066B` を認識。その後の診断版ではUSB未認識との報告 |
| Mass Storage / Windows起動 | 未確認 |

以前の**タイマー診断版**は、UEFI内部に残っていたWatch 3由来の割り込み番号をCP2AのDTBに合わせて修正したものです。[ビルド結果と成果物（Run 36560298201）](https://github.com/TeamWearFreedomProject/mu_Aurora-eos_platforms/actions/runs/36560298201)は成功していますが、実機では暗転と同じWinUSB認識が続きました。成功したビルドは実機での安全性や動作を保証しません。

## リポジトリの見方

- **`Aurora&eos-port`**：Watch 2移植の作業ブランチ。いま読んでいるREADMEはこちらです。
- **`main`**：元のWatch 3向けコードが中心の古いブランチ。現在のデフォルトブランチです。
- [詳しい技術メモ](Platforms/AuroraPkg/README.md)：CP2A画像の解析、メモリマップ、ACPI、未解決点。
- [実機観測の記録](Platforms/AuroraPkg/Research/hardware_observation_2026-09-29_ufp.json)：一時起動とUSB認識。端末固有のシリアル番号は含みません。

## 2026-09-30の診断更新

タイマー診断版は暗転とUFPらしいUSB認識が続きました。設定画面直行版では青い目印の後に暗転し、USBも認識されなくなったとの報告があります。この直行版は誤って `boot_b` に書き込まれ、その後、所有者が純正bootを戻しました。

青保持版では、青い表示が約60秒維持され、USBは認識されなかったとの報告があります。現在は設定画面の初期化を数字と色で区切る診断版です。[番号の対応と観測方法](Platforms/AuroraPkg/Research/frontpage_numbered_stages_2026-09-30.md)を参照してください。この版は2026-10-01に実機で8まで進み、その表示が残り、USBは未認識との報告がありました。

8の後の警告・認証・メニュー描画を細分した診断版は実機で23に到達し、その表示が残ったとの報告がありました。これは認証失敗の分岐を通った証拠で、パスワード設定や入力待ち到達の証拠ではありません。[細分番号の対応](Platforms/AuroraPkg/Research/frontpage_ui_substages_2026-10-01.md)を参照してください。現在は認証の返り値の分類を下段に表示し、パスワード画面の準備・描画・入力待ちを上段の数字で細分する診断版です。[2段表示と番号の対応](Platforms/AuroraPkg/Research/frontpage_password_status_2026-10-01.md)を参照してください。この版は実機で上段82・下段62が残ったとの報告がありました。初回認証がデバイスエラーを返し、画面のテーマ設定が戻ったことを示します。

現在はパスワード画面の文字・入力欄・ボタン作成と枠描画を3桁の上段番号で細分した診断版です。[番号と観測方法](Platforms/AuroraPkg/Research/frontpage_password_controls_2026-10-01.md)を参照してください。この版は実機で上段132・下段62が残ったとの報告がありました。現在は文字表示版で、処理名・呼び出し前後・初回認証と直近のUI処理の返り値を表示します。[文字表示と新しい境界番号](Platforms/AuroraPkg/Research/frontpage_text_diagnostic_2026-10-01.md)を参照してください。成果物名は `aurora-CP2A-default-control-diagnostic-UNVERIFIED` です。写真で137（SET DEFAULTの直前）とキャンセル登録成功を確認しました。現在は既定ボタン設定の内部を171–178で分ける版です。[内部の番号と観測方法](Platforms/AuroraPkg/Research/frontpage_default_control_2026-10-01.md)を参照してください。原因はまだ確定していません。

## 次に調べること

1. 実機の現在のファームウェア・スロット・復旧手段を再確認する。
2. 文字表示診断版を一時起動し、約4分待って最後に残った番号・処理名・エラー名を記録する。動画は不要。
3. 最後に見えた番号の前後にある処理を重点的に切り分ける。

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
