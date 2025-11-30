// Googleカレンダーの更新をトリガーに実行される関数
function sendCalendarNotification(e) {
  
  // ▼▼▼ Google Chatで取得した自身のWebhook URLに書き換える ▼▼▼
  const webhookUrl = "ここにWebhook URLを貼り付け";
  // ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲

  // 1. どのカレンダーで予定が更新されたか特定する
  const calendar = CalendarApp.getCalendarById(e.calendarId);

  // 2. そのカレンダーから、直近で作成された予定を1件見つけ出す
  let latestEvent = null;
  let latestCreationTime = new Date(0); 

  const oneDayAgo = new Date();
  oneDayAgo.setDate(oneDayAgo.getDate() - 1);
  const events = calendar.getEvents(oneDayAgo, new Date(Date.now() + 1000 * 60 * 60 * 24 * 365));

  for (const event of events) {
    if (event.getDateCreated() > latestCreationTime) {
      latestCreationTime = event.getDateCreated();
      latestEvent = event;
    }
  }
  
  // もし最新の予定が見つからなかった場合は、ここで処理を終了する
  if (latestEvent === null) {
    return;
  }

  // ★★★ 追加：本当に新しい予定かを確認する処理 ★★★
  // これが無いと、新しい予定追加の度に、24時間以内に作成された予定の通知がきちゃう。
  const now = new Date();
  const creationTime = latestEvent.getDateCreated();
  const diffSeconds = (now.getTime() - creationTime.getTime()) / 1000;

  // 作成されてから60秒以上経っている場合は、編集・削除とみなし通知しない
  if (diffSeconds > 60) {
    return; 
  }
  
  // 3. 予定の詳細情報を取得する
  const who = latestEvent.getCreators().join(', ');
  const title = latestEvent.getTitle();
  const startTime = new Date(latestEvent.getStartTime()).toLocaleString('ja-JP');
  const endTime = new Date(latestEvent.getEndTime()).toLocaleString('ja-JP');

  // 4. Chatに送信するメッセージを組み立てる（太字の記号を * に修正）
  const messageText = `新しい予定が追加されました
---
*作成者:* ${who}
*タイトル:* ${title}
*日時:* ${startTime} - ${endTime}`;

  const message = {
    "text": messageText
  };

  const options = {
    "method": "post",
    "contentType": "application/json; charset=UTF-8",
    "payload": JSON.stringify(message)
  };

  UrlFetchApp.fetch(webhookUrl, options);
}
