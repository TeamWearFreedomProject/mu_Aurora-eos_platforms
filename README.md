# KyogoのPixel Watch 2 UEFI移植プロジェクト

**Kyogoが企画・実機検証・開発の進行を担当している、Pixel Watch 2 Wi-Fi向けのUEFI移植プロジェクトです。**  
UEFIからLinuxカーネルを起動し、再現できる形で共有することを目指しています。

> ⭐︎ ChatGPT／Codexと協力して開発中。コード・解析・診断・文書作成にもAIの支援を使っています。完成版や個別サポートは約束できません。

## ここまでの成果 — 2026-10-01

暗転だけの状態から、実機の処理を数字と文字で追えるようになりました。

- Aurora向けUEFIのビルドとイメージ構造検査が成功。
- 複数の診断版がPixel Watch 2実機の一時起動で受理された。
- 最新の実機写真は **214 / BUTTON TEXT / BEFORE CALL**。
- OKボタンの枠描画は戻り、背景塗りつぶしは **EFI_SUCCESS**。文字描画から戻った表示は未確認。
- 初回認証のEFI_DEVICE_ERRORを確認。描画の返り値とは別に調査中。

**設定画面の完成、Mass Storage、このUEFIからのLinux・Windows起動はまだ確認できていません。**

## 詳細と成果物

- [**Watch 2移植のREADME**](https://github.com/TeamWearFreedomProject/mu_Aurora-eos_platforms/blob/Aurora%26eos-port/README.md)
- [**実機結果と診断の歩み**](https://github.com/TeamWearFreedomProject/mu_Aurora-eos_platforms/blob/Aurora%26eos-port/PROGRESS.md)
- [最新の成功ビルドと成果物](https://github.com/TeamWearFreedomProject/mu_Aurora-eos_platforms/actions/runs/36820130452)

最新の `aurora-CP2A-string-window-diagnostic-UNVERIFIED` は、文字描画の内部をさらに分ける版です。ビルド・構造検査は成功していますが、この新しい版の実機結果は未確認です。成果物は研究用の一時起動候補です。

**作業コードは[`Aurora&eos-port`ブランチ](https://github.com/TeamWearFreedomProject/mu_Aurora-eos_platforms/tree/Aurora%26eos-port)にあります。** この `main` のコードは元のWatch 3向け構成が中心です。Watch 3向けバイナリをWatch 2用と取り違えないでください。

## 開発者と謝辞

Watch 2移植の企画・開発の進行・実機検証は **Kyogo** が担当しています。

コードの土台は[WOA-Project / mu_seluna_platforms](https://github.com/WOA-Project/mu_seluna_platforms)・DuoWoA authorsと、Microsoftの[Project Mu](https://microsoft.github.io/mu/)です。[PixelWatch-Guides](https://github.com/WOA-Project/PixelWatch-Guides)も参考にしています。

[**作者・参考資料・元プロジェクトの協力者への謝辞**](https://github.com/TeamWearFreedomProject/mu_Aurora-eos_platforms/blob/Aurora%26eos-port/CREDITS.md)

既存コードの著作権とライセンスを保持しています。このWatch 2移植を元プロジェクトが承認・保証しているという意味ではありません。
