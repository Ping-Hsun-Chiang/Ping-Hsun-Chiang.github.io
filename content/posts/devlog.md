---
title: "從零打造全端電商：Next.js + Supabase 開發紀錄"
date: 2026-05-02
draft: false
category: "專案紀錄"
---

第一次從頭到尾獨立完成一個有前台、後台、資料庫、部署的完整網站。這篇文章記錄開發過程、遇到的問題，以及這次學到的東西。

## 專案目標

做一個服飾電商網站，功能包含：

- **顧客前台**：瀏覽商品、選規格加入購物車、填資料結帳、選 7-11 取貨門市
- **管理後台**：登入保護、管理商品與規格（含庫存售價）、查看及處理訂單

技術選擇以「免費、現代、全端 TypeScript」為原則，最後選用 Next.js 16 + Supabase + Tailwind CSS 組合。

---

## 開發歷程

### Phase 1：環境建置 & 資料庫設計

第一步是在 WSL（Windows Subsystem for Linux）上把 Node.js、Git、GitHub CLI 都裝起來。聽起來很基本，但光這步就踩了不少坑（詳見下方）。

資料庫設計了四張表：

```
products          商品主檔
product_variants  商品規格（一個商品對應多個規格）
orders            訂單主檔
order_items       訂單明細（一筆訂單對應多個商品）
```

並在 Supabase 設定 Row Level Security（RLS）：匿名使用者只能讀商品、寫訂單；管理員才能做所有操作。

### Phase 2：管理後台

後台使用 Next.js 的 route group 區分「登入頁」和「受保護頁面」：

```
admin/(auth)/login    不需驗證
admin/(dashboard)/    layout 會檢查登入狀態
```

商品管理支援：新增 / 編輯 / 刪除商品，以及每個商品的多個規格（SKU、顏色、尺寸、庫存、售價）。全部使用 Server Actions 處理資料寫入，不需要自己架 API。

### Phase 3：顧客前台

首頁列出所有上架商品，如果一個商品有多個規格價格不同，就顯示「NT$XXX 起」。

商品詳情頁的規格選擇邏輯：先選顏色再選尺寸，缺貨的規格自動變成灰色不可點擊。購物車用 Zustand 管理，並搭配 `persist` middleware 存到 localStorage，重新整理後資料不會消失。

一個有趣的細節：購物車圖示顯示數量時，因為 SSR 階段 localStorage 還不可用，會出現 hydration mismatch 的問題。解法是用 `useState(false)` + `useEffect` 確認在 client 端才顯示數量。

### Phase 4：結帳流程

這階段最複雜的部分有兩個：

**7-11 門市選擇**：7-11 的 E-map 是用 `window.open` 開一個 popup，選完門市後用 `postMessage` 把門市資料傳回父視窗。開發環境做了一個模擬 popup 頁面，用相同的 postMessage 介面對接。

**原子下單**：為了防止超賣，不能「先讀庫存、再下單」分兩步走，必須在一個 transaction 裡完成。Supabase 不支援直接的 multi-step transaction，所以寫了一個 PostgreSQL RPC 函式 `create_order_and_update_stock`，在 DB 端處理：鎖定列 → 驗證庫存 → 建立訂單 → 扣減庫存。另外，售價從資料庫讀取而不信任前端傳來的值，防止使用者竄改金額。

### Phase 5：訂單管理

後台訂單列表支援依狀態篩選，使用 URL searchParams 傳遞狀態參數，這樣篩選結果可以直接分享網址。

訂單詳情頁顯示客戶資訊、取貨門市和商品明細，並提供狀態更新表單。有一個「管理員備註」欄位專門用來記錄賣貨便的交貨便服務代碼。

---

## 踩過的坑

### WSL DNS 失效

第一次 `npm install` 直接失敗，原因是 `/etc/resolv.conf` 不存在，WSL 根本無法解析網域名稱。

```bash
sudo sh -c 'echo "nameserver 8.8.8.8\nnameserver 1.1.1.1" > /etc/resolv.conf'
```

手動設定 DNS 才解決。

### GitHub CLI 安裝失敗

照官方文件安裝 GitHub CLI，`apt-get update` 直接噴錯。原因是 `echo` 指令把安裝來源 URL 換行了，寫入 `sources.list` 的內容是壞掉的。刪掉重建後才正常。

### Supabase TypeScript 型別全變 `never`

加入 TypeScript 型別之後，所有 Supabase 查詢的回傳型別都變成 `never`，什麼都用不了。

原因是 `@supabase/postgrest-js` v2 的型別系統要求每張表都要有 `Relationships: []` 欄位，以及 schema 層級要有 `Views`、`Functions`、`Enums`、`CompositeTypes` 等欄位，少一個就整個壞掉。補齊這些欄位之後才恢復正常。

### Next.js 16 的 `middleware.ts` 被棄用

標準的 `middleware.ts` + `export { ... as middleware }` 在 Next.js 16 變成 deprecated，改成要用 `proxy.ts` + `export { ... as proxy }`。沒改的話會一直收到警告。

### Vercel 部署後白畫面

部署成功，點網址卻顯示「A server error occurred」。原因很簡單：`.env.local` 被 `.gitignore` 排除在外，Supabase 的 URL 和 anon key 沒有被帶到 Vercel。在 Vercel Dashboard 的 Environment Variables 手動填入後，重新部署就正常了。

---

## 這次學到的東西

**Server Components vs Client Components 的邊界**

Next.js App Router 預設所有元件都是 Server Component。只有需要用到 `useState`、`useEffect`、事件處理器的元件，才需要在檔案最上面加 `'use client'`。理解這個邊界之後，就能知道哪些資料抓取可以直接在元件裡做（server），哪些需要另外的狀態管理（client）。

**Server Actions 取代 API Routes**

以前要做資料寫入，需要自己寫 `app/api/xxx/route.ts`，前端再 fetch 去呼叫。現在用 Server Actions，直接在 `.ts` 檔案頂部寫 `'use server'`，然後從前端直接呼叫這個函式，Next.js 自動處理底層通訊。少了很多樣板程式碼。

**RLS 是資料庫層的安全網**

Row Level Security 讓你在資料庫層面定義「誰可以讀 / 寫哪些資料」，就算前端程式碼有漏洞，資料庫本身還是有一層保護。匿名使用者只能讀商品和寫自己的訂單，無論怎麼操作 API 都無法存取其他人的資料。

**原子性交易的重要性**

超賣問題不能靠「讀完再寫」解決，因為兩個請求可能同時讀到同一個庫存數字。正確做法是在資料庫端用 transaction + row lock，讓同時進來的請求排隊等待，確保庫存計算的原子性。

**Zustand 的 persist middleware**

購物車需要在重新整理後保留，用 Zustand 的 persist middleware 搭配 localStorage 可以很簡單做到，不需要手動讀寫 localStorage。但要注意 SSR 環境沒有 localStorage，需要處理 hydration 問題。

---

## 結語

這個專案從環境建置到正式部署，整個走了一遍全端開發的流程。最大的收穫是理解了「前台 / 後台 / 資料庫 / 部署」各層之間怎麼串接，以及每一層分別負責什麼事情。

踩的坑大多是環境問題和套件版本問題，和核心的業務邏輯比起來反而花了更多時間。下次建新專案大概可以少踩一半。
