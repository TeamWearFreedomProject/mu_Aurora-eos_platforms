# KyogoのPixel Watch 2 UEFI移植プロジェクト

**Kyogoが進めている、Pixel Watch 2 Wi-Fi向けのUEFI移植プロジェクトです。**  
目標は、UEFIからLinuxカーネルを起動し、再現できる形で他の人にも共有すること。

> ⭐︎ ChatGPT／Codexと協力して、学習・実験として開発しています。Kyogoが企画・実機検証・開発の進行を担当し、AIがコード・解析・診断・文書作成を支援しています。開発途中なので、完成版や個別サポートは約束できません。

This is an experimental Pixel Watch 2 Wi-Fi (aurora) UEFI port led and hardware-tested by **Kyogo**, with ChatGPT/Codex assistance. It builds on WOA-Project's Pixel Watch 3 port and Project Mu. A working settings menu and Linux boot through this port are not yet confirmed.

## ここまでの成果 — 2026-10-03

**暗転だけの状態から、UEFI内の「OKボタンの文字描画直前」まで処理を追跡できるようになりました。**

| 項目 | 現在の状態 |
| --- | --- |
| Aurora向けUEFIのビルド | GitHub Actionsで成功 |
| CP2A由来のメモリ配置・CPU・タイマー・一部ACPI | 静的解析とCIで検査。実機での完全な正しさは未確認 |
| 実機への一時起動 | 複数の診断候補が受理された |
| 実機の診断表示 | 数字だけでなく処理名・呼び出し前後・エラー名・生の値を表示 |
| 最新の実機結果 | **273 / FONT STRING IMAGE / BEFORE CALL**。描画開始通知はEFI_SUCCESS。HII文字描画から戻った表示は未確認 |
| 初回認証 | EFI_DEVICE_ERRORを確認。内部原因は未確定 |
| 設定画面・入力・Mass Storage | 未確認 |
| このUEFIからのLinux / Windows起動 | 未確認 |

214の先に進んで273を表示しました。HIIの文字描画関数の直前まで確認できましたが、その内部の停止箇所はまだ未確定です。

[**実機結果と診断の歩みを読む**](PROGRESS.md)

## 最新の診断版

[成功したビルドと成果物（Run 37091240025）](https://github.com/TeamWearFreedomProject/mu_Aurora-eos_platforms/actions/runs/37091240025)

GitHubにログインし、ページ下部のArtifactsから `aurora-CP2A-hii-font-diagnostic-UNVERIFIED` を選びます。HIIの文字描画内部を301–322で分けた版です。

**この版はビルド・構造検査まで成功しています。301–322の実機結果は未確認です。**

対象は **Pixel Watch 2 Wi-Fi / aurora**、解析対象の純正ファームウェアは **CP2A.260603.001.S1**。実機をこの版へ戻したとの記録はありますが、ADBによる再確認は未実施です。eos（LTE）での動作も未確認です。

診断候補は研究用です。**一時起動の `fastboot boot` 用として扱い、永続パーティションへ書き込まないでください。** Pixel Watch 3向けのガイドやバイナリをWatch 2の互換手順として使わないでください。

## 次の目標

1. 文字描画の内部でどの処理が戻らないか、実機表示とソースを照合する。
2. 設定画面と入力操作、起動経路を再現できるようにする。
3. このUEFIからAurora用Linuxカーネルへ制御を渡し、起動ログで確認する。

LinuxLoaderは含まれていますが、現在は `BootIntoFastboot = TRUE` に固定されています。通常のLinux起動経路をそのまま使える状態ではなく、この実機で選択・実行された証拠もありません。

## 開発した人・参考にした人

**このWatch 2移植の企画・開発の進行・実機検証：Kyogo。**

土台は[WOA-Project / mu_seluna_platforms](https://github.com/WOA-Project/mu_seluna_platforms)のPixel Watch 3向け移植と、Microsoftの[Project Mu](https://microsoft.github.io/mu/)です。[PixelWatch-Guides](https://github.com/WOA-Project/PixelWatch-Guides)も参考にしています。

元プロジェクトの作者と協力者への謝辞、AI支援の範囲、ライセンスは[**CREDITS.md**](CREDITS.md)にまとめています。既存コードの著作権表示は保持しています。

## リポジトリと技術資料

- **`Aurora&eos-port`**：Watch 2移植の作業ブランチ。このREADMEの内容はこちらのコードが対象。
- **`main`**：紹介ページを置いているデフォルトブランチ。コードは元のWatch 3向け構成が中心。
- [進捗と実機結果](PROGRESS.md)
- [Auroraの技術メモ](Platforms/AuroraPkg/README.md)
- [最新のHII描画診断メモ](Platforms/AuroraPkg/Research/frontpage_hii_font_2026-10-03.md)
- [GitHub Actionsのビルド定義](.github/workflows/aurora-build.yml)

ローカルビルドは、依存環境とサブモジュールを用意して `bash ./build_fd_aurora.sh` を実行します。詳しくは技術メモを参照してください。
