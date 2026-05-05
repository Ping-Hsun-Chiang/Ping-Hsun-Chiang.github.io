---
title: "Golang Programming Learning Journey"
date: 2026-04-10
draft: false
category: "學習筆記"
---

## 背景與開發環境

因為手邊目前僅有一台老舊的 Acer 筆電，為了在硬體資源受限的情況下維持高效的開發節奏，我採用了「在 WSL (Linux) 環境中撰寫程式碼，並編譯為 Windows 原生執行檔」的開發策略。

這種方式讓我既能享受 Linux 強大且靈活的終端機與開發工具鏈（如 Git, Docker），又能直接在 Windows 主機上測試最終產物。

以下是我建立第一個 Go 語言 2D 遊戲（使用 Ebitengine）的環境建置與測試過程記錄。

---

## Step 1: 在 WSL 安裝 Golang 環境

首先，在 WSL 的終端機中下載並安裝 Go 1.22.2 版本，並設定環境變數。

```bash
# 下載 Go 安裝包
wget [https://go.dev/dl/go1.22.2.linux-amd64.tar.gz](https://go.dev/dl/go1.22.2.linux-amd64.tar.gz)

# 移除舊版本並解壓縮新版本至 /usr/local
sudo rm -rf /usr/local/go && sudo tar -C /usr/local -xzf go1.22.2.linux-amd64.tar.gz

# 清理安裝包
rm go1.22.2.linux-amd64.tar.gz

# 將 Go 路徑加入環境變數
echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
echo 'export GOPATH=$HOME/go' >> ~/.bashrc

# 重新載入設定
source ~/.bashrc

# 驗證安裝結果
go version
# 預期輸出: go version go1.22.2 linux/amd64
```

## Step 2: 建立專案與初始化模組

建立遊戲專案目錄，初始化 Git 數據庫與 Go Modules，並下載開源的 2D 遊戲引擎 Ebitengine。

```bash
# 建立並進入專案資料夾
mkdir -p ~/game_projects/test_game
cd ~/game_projects/test_game

# 初始化 Git 與 Go Mod
git init
go mod init test_game

# 取得 ebiten 遊戲引擎套件
go get [github.com/hajimehoshi/ebiten/v2](https://github.com/hajimehoshi/ebiten/v2)
```

## Step 3: 撰寫遊戲主程式架構

建立 ```main.go``` 檔案。這是一個非常基礎的 Ebiten 遊戲迴圈（Game Loop）架構，會在畫面上填滿深綠色背景，並印出測試文字。

```go
package main

import (
	"image/color"
	"log"

	"[github.com/hajimehoshi/ebiten/v2](https://github.com/hajimehoshi/ebiten/v2)"
	"[github.com/hajimehoshi/ebiten/v2/ebitenutil](https://github.com/hajimehoshi/ebiten/v2/ebitenutil)"
)

// Game 實作 ebiten.Game 介面
type Game struct{}

// Update 處理遊戲邏輯更新
func (g *Game) Update() error {
	return nil
}

// Draw 處理畫面渲染
func (g *Game) Draw(screen *ebiten.Image) {
	// 填滿背景顏色
	screen.Fill(color.RGBA{0, 100, 0, 255})
	
	// 在畫面上印出 Debug 資訊
	ebitenutil.DebugPrint(screen, "Simulation Ready!\nEngine: Ebitengine\nRunning on Native Windows!")
}

// Layout 定義遊戲視窗尺寸
func (g *Game) Layout(outsideWidth, outsideHeight int) (screenWidth, screenHeight int) {
	return 640, 480
}

func main() {
	// 設定視窗大小與標題
	ebiten.SetWindowSize(640, 480)
	ebiten.SetWindowTitle("My Go Game")

	// 啟動遊戲
	if err := ebiten.RunGame(&Game{}); err != nil {
		log.Fatal(err)
	}
}
```

## Step 4: 撰寫 Makefile 自動化編譯

為了方便後續開發，我寫了一個 Makefile。其中最關鍵的是 build 指令裡的 GOOS=windows 參數，這能讓 Go 編譯器在 Linux 環境下直接打包出 Windows 可執行的 .exe 檔案。

建立 ```Makefile``` 檔案：

```Makefile
.PHONY: run build clean

run: build
	./game.exe

build:
	# 進行交叉編譯，關閉 CGO，指定目標作業系統為 Windows
	CGO_ENABLED=0 GOOS=windows GOARCH=amd64 go build -ldflags="-s -w" -o game.exe main.go

clean:
	rm -f game.exe
```

## Step 5: 編譯與執行

最後，只需要在終端機輸入一行指令，即可完成編譯並直接在 Windows 中呼叫執行檔彈出遊戲視窗！

```bash
make run
```