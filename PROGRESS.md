# Pixel Watch 2 UEFI移植の進捗

**開発・実機検証：Kyogo**  
更新：2026-10-01（日本時間）

## いま確認できている成果

Aurora向けUEFIをビルドし、Pixel Watch 2実機の一時起動で、設定画面の認証・ボタン作成・描画処理まで進むことを確認しています。GOPに直接描いた番号・処理名・EFIステータスを使って、暗転だけでは分からなかった処理の境界を追えるようになりました。

最新の実機写真は **214 / BUTTON TEXT / BEFORE CALL**。その時点で **BUTTON FILL / EFI_SUCCESS** が表示され、OKボタンの枠描画が戻ったことと、背景の塗りつぶしが成功を返したことが分かっています。文字描画から戻った215は未確認です。

これは「UEFIメニューが完成した」という成果ではありません。現時点では文字描画の境界に調査対象を絞った段階です。

## 実機で追った境界

以下は別々の診断版で最後に確認した表示です。番号の大小は完成度や同一ビルド内の進行順を示しません。

| 診断・観測 | 分かったこと | 記録 |
| --- | --- | --- |
| ロゴが一瞬出て暗転 | 画面の変化は見えるが、その後の処理が分からなかった | [最初の実機観測](Platforms/AuroraPkg/Research/hardware_observation_2026-09-29_ufp.json) |
| 青い表示が約60秒残る | 診断表示を保持できた。CPUの継続動作やUEFI全体の安定性は未証明 | [番号付き診断](Platforms/AuroraPkg/Research/frontpage_numbered_stages_2026-09-30.md) |
| 8 → 23 | 設定画面の初期化と認証失敗分岐の境界を追跡 | [UI処理の細分](Platforms/AuroraPkg/Research/frontpage_ui_substages_2026-10-01.md) |
| 上段82・下段62 | 初回認証がEFI_DEVICE_ERRORを返したことを分類表示で確認 | [認証診断](Platforms/AuroraPkg/Research/frontpage_password_status_2026-10-01.md) |
| 上段132・下段62 | キャンセルボタン作成から戻った境界を確認。作成成功自体はこの表示だけでは断定しない | [部品作成診断](Platforms/AuroraPkg/Research/frontpage_password_controls_2026-10-01.md) |
| 137 / SET DEFAULT | キャンセル登録はEFI_SUCCESS。既定ボタン設定の直前まで到達 | [文字表示](Platforms/AuroraPkg/Research/frontpage_text_diagnostic_2026-10-01.md) |
| 176 / BUTTON DRAW | ボタン検索を通過し、状態変更から戻った。描画の直前まで到達 | [既定ボタン診断](Platforms/AuroraPkg/Research/frontpage_default_control_2026-10-01.md) |
| **214 / BUTTON TEXT** | **枠描画が戻り、背景塗りつぶしはEFI_SUCCESS。文字描画から戻った表示は未確認** | [ボタン描画診断](Platforms/AuroraPkg/Research/frontpage_button_draw_2026-10-01.md) |

## 初回認証のエラーと描画の停止を区別する

AUTH RESULTの **EFI_DEVICE_ERROR / 8000000000000007** は、最初の認証呼び出しの結果です。パスワードが設定済みであることや、文字描画がこのエラーを返したことを示しません。エラーの内部原因は未確定です。

UI欄は直近の追跡対象の返り値です。214の写真では背景塗りつぶしの成功を示しており、文字描画の結果はまだありません。呼び出しが戻らなければ、その返り値を記録することもできません。

「BEFORE CALL」は次の呼び出しより前に表示し、約2秒の診断待ち時間を置いています。静止した表示だけで、CPUが動き続けていることや次の関数に入ったことまでは断定できません。描画と待ち時間自体の影響も含めて調べます。

## 次に試す診断版

[最新の成功ビルド・成果物](https://github.com/TeamWearFreedomProject/mu_Aurora-eos_platforms/actions/runs/36820130452)  
成果物名：`aurora-CP2A-string-window-diagnostic-UNVERIFIED`

StringToWindow内部の3つの処理を分けています。

| 呼び出し前 | 戻った後 | 処理 |
| --- | --- | --- |
| 271 | 272 | 描画開始通知 |
| 273 | 274 | HIIフォントによる文字描画（StringToImage） |
| 275 | 276 | 描画終了通知 |

**ビルド・構造検査は成功。新しい271–276の実機結果は未確認です。** 詳細は[診断メモ](Platforms/AuroraPkg/Research/frontpage_string_window_2026-10-01.md)を参照してください。

## 未確認の項目

- 安定した設定画面と入力操作
- 現在の診断版でのUSB機能
- Watch 2でのMass Storage
- このUEFI移植からのLinuxカーネル起動
- Windows起動

以前の版のUSB `045E:066B` 認識は記録していますが、その後の診断版ではUSB未認識との報告です。Mass Storageの成功やUSB停止原因の特定には結び付けていません。

## 目標

まず設定画面の停止原因を絞り、再現できるUEFI起動経路を作ります。その後、Aurora向けLinuxカーネルへ制御が渡ったことを起動ログで確認するのが最初の大きな節目です。現在共有しているものは、その途中の研究記録と診断用コードです。

[開発者・元プロジェクト・謝辞](CREDITS.md) / [README](README.md)
