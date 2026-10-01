# Credits / 謝辞

## このWatch 2移植を進めている人

**Kyogo — プロジェクトの企画・開発の進行・Pixel Watch 2実機での検証・結果の記録。**

このリポジトリは、KyogoがChatGPT／Codexの支援を受けて進めている個人の学習・実験プロジェクトです。AIはコード変更、ソース解析、診断用ビルド、文書作成を支援しています。実機の操作と観測結果はKyogoが提供しています。完成版の提供や個別サポートは約束していません。

この移植で追加したAurora向け設定・検査・診断と、土台となる既存実装の作者は区別しています。既存コードの著作権やライセンスをKyogoに置き換えるものではありません。

## コードの土台と参考資料

| プロジェクト・作者 | この移植との関係 |
| --- | --- |
| [WOA-Project / mu_seluna_platforms](https://github.com/WOA-Project/mu_seluna_platforms)・DuoWoA authors | Pixel Watch 3向けUEFI移植。コード・プラットフォーム構成・ビルド方法の土台 |
| [WOA-Project / PixelWatch-Guides](https://github.com/WOA-Project/PixelWatch-Guides)・The Duo WOA Authors | UEFI起動とMass Storageの仕組み・画面を理解するための参考資料。Watch 2への互換性を保証する資料ではない |
| [Microsoft / Project Mu](https://microsoft.github.io/mu/) | UEFI基盤とビルド環境 |
| [Microsoft / mu_plus](https://github.com/microsoft/mu_plus) | 設定画面、UIツールキット、ウィンドウ管理など。現在の描画診断はこの実装を調査している |
| [Microsoft / mu_basecore](https://github.com/microsoft/mu_basecore) と [TianoCore / EDK II](https://github.com/tianocore/edk2) | 継承しているUEFIの基盤 |
| [Microsoft / mu_feature_dfci](https://github.com/microsoft/mu_feature_dfci) | 設定・認証処理。初回認証エラーの調査対象 |
| Google / Android Open Source Project | Pixel Watch 2の純正ファームウェア・デバイスツリーを解析資料として参照 |

上記の開発者が本プロジェクトに直接参加したり、本移植を承認したりしているという意味ではありません。

## 元プロジェクトから引き継ぐ謝辞

[mu_seluna_platformsのAcknowledgements](https://github.com/WOA-Project/mu_seluna_platforms#acknowledgements)に記載されている方々への謝辞も引き継ぎます。

- [EFIDroid Project](http://efidroid.org)
- [Andrei Warkentin / RaspberryPiPkg](https://github.com/andreiw/RaspberryPiPkg)
- Sarah Purohit
- [Googulator](https://github.com/Googulator/)
- [Ben (Bingxing) Wang / imbushuo](https://github.com/imbushuo/)
- [Samuel Tulach / Rainbow Patcher](https://github.com/SamuelTulach/rainbow)

この一覧は元プロジェクトの謝辞に基づくもので、各人のWatch 2移植への直接参加を示すものではありません。

## ライセンス・著作権

[LICENSE](LICENSE)と各ソースファイルの著作権表示・SPDX表記を保持しています。ファイルごとのライセンスが適用されます。継承したNOTICEやバイナリの権利表示も確認してください。

[QualcommモジュールのNOTICE](Platforms/QcomModulePkg/NOTICE) / [UFPのLICENSE](Platforms/SelunaPkg/UFP/LICENSE.md)
