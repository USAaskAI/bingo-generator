#!/usr/bin/env python3
"""
シンプルHTTPサーバで1つのPythonスクリプトとして動作するビンゴカードジェネレータ
依存なし（標準ライブラリのみ）
ブラウザで http://localhost:8000 を開くとアプリが動作します
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver

# HTMLテンプレートを直接レスポンスする
HTML = r'''<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>ビンゴカードジェネレータ (MVP)</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 800px; margin: auto; padding: 20px; }
    #input-area, #actions, #preview { margin-bottom: 20px; }
    #sortable-list { list-style: none; padding: 0; }
    #sortable-list li { padding: 8px; margin: 4px 0; background: #f0f0f0; border: 1px solid #ccc; cursor: grab; }
    #grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 4px; }
    .cell { position: relative; padding: 20px 0; border: 1px solid #000; text-align: center; cursor: pointer; user-select: none; min-height: 80px; }
    .overlay { position: absolute; top: 4px; right: 4px; font-size: 24px; pointer-events: none; }
    h2 { margin: 16px 0 8px; }
  </style>
</head>
<body>
  <h1>ビンゴカードジェネレータ (MVP)</h1>
  <div id="input-area">
    <textarea id="text-input" rows="9" style="width:100%;" placeholder="各行に1セル分のテキストを入力">1&#10;2&#10;3&#10;4&#10;5&#10;6&#10;7&#10;8&#10;9</textarea>
    <ul id="sortable-list"></ul>
  </div>
  <div id="actions">
    <button id="reset">リセット</button>
    <button id="shuffle">シャッフル</button>
    <button id="download">ダウンロード (PNG)</button>
  </div>
  <div id="preview">
    <h2>ビンゴプレビュー</h2>
    <div id="grid"></div>
  </div>
  <script src="https://cdn.jsdelivr.net/npm/sortablejs@latest/Sortable.min.js"></script>
  <script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>
  <script>
    window.addEventListener('DOMContentLoaded', () => {
      const textInput = document.getElementById('text-input');
      const listEl = document.getElementById('sortable-list');
      const gridEl = document.getElementById('grid');
      const resetBtn = document.getElementById('reset');
      const shuffleBtn = document.getElementById('shuffle');
      const downloadBtn = document.getElementById('download');
      
      let items = [];
      let marks = [];

      function init() {
        // 初期テキスト読み込み
        const lines = textInput.value.split('\n').slice(0,9);
        items = lines.concat(Array(9-lines.length).fill(''));
        marks = Array(9).fill('');
        render();
      }

      function render() {
        // リスト更新
        listEl.innerHTML = '';
        items.forEach((text, idx) => {
          const li = document.createElement('li');
          li.textContent = text || '(空)';
          listEl.appendChild(li);
        });
        // グリッド更新
        gridEl.innerHTML = '';
        items.forEach((text, idx) => {
          const cell = document.createElement('div');
          cell.className = 'cell';
          cell.textContent = text || '\u00A0';
          if (marks[idx]) {
            const overlay = document.createElement('span');
            overlay.className = 'overlay';
            overlay.textContent = marks[idx];
            cell.appendChild(overlay);
          }
          cell.addEventListener('click', () => {
            marks[idx] = marks[idx] === '⭕' ? '' : '⭕';
            render();
          });
          gridEl.appendChild(cell);
        });
      }

      // テキスト入力時
      textInput.addEventListener('input', () => {
        const lines = textInput.value.split('\n').slice(0,9);
        items = lines.concat(Array(9-lines.length).fill(''));
        render();
      });
      
      // 並び替え初期化
      new Sortable(listEl, {
        animation: 150,
        onEnd: evt => {
          const [m] = items.splice(evt.oldIndex,1);
          items.splice(evt.newIndex,0,m);
          const [mk] = marks.splice(evt.oldIndex,1);
          marks.splice(evt.newIndex,0,mk);
          render();
        }
      });

      resetBtn.addEventListener('click', () => {
        marks = Array(9).fill('');
        render();
      });

      shuffleBtn.addEventListener('click', () => {
        for (let i=items.length-1;i>0;i--) {
          const j = Math.floor(Math.random()*(i+1));
          [items[i],items[j]] = [items[j],items[i]];
          [marks[i],marks[j]] = [marks[j],marks[i]];
        }
        render();
      });

      downloadBtn.addEventListener('click', () => {
        html2canvas(gridEl).then(canvas => {
          const link = document.createElement('a');
          link.download = 'bingo.png';
          link.href = canvas.toDataURL('image/png');
          link.click();
        });
      });

      init();
    });
  </script>
</body>
</html>'''

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(HTML.encode('utf-8'))

if __name__ == '__main__':
    port = 8000
    print(f'Serving at http://localhost:{port}')
    with HTTPServer(('', port), Handler) as httpd:
        httpd.serve_forever()
