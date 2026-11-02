# Instagram Autopilot (Syed Automation)

Roz khud chalta hai: trend + competitor analysis, post idea, caption + hashtags, image, Instagram par post, aur Telegram par progress report.

## Setup (ek baar)

1. **GitHub:** naya **public** repo banao aur is folder ki saari files upload karo. (Public isliye ki Instagram image ko link se uthata hai. Keys kabhi files mein mat likhna, sirf Secrets mein.)
2. **Instagram:** account ko Professional (Business/Creator) banao aur Facebook Page se jodo.
3. **Meta access:** developers.facebook.com par app banao. Graph API Explorer se token lo jisme ye permissions hon: `instagram_basic`, `instagram_content_publish`, `instagram_manage_insights`, `pages_show_list`, `pages_read_engagement`. Isse long-lived token banao, phir Page token lo (wo expire nahi hota). Phir `me/accounts?fields=instagram_business_account` se **Instagram user ID** lo. (Meta ke menus badalte rehte hain, to docs dekh lena.)
4. **Claude API key:** console.anthropic.com se banao.
5. **Telegram:** @BotFather se bot banao (token milega). Bot ko ek message bhejo, phir `https://api.telegram.org/bot<TOKEN>/getUpdates` se apna chat id lo.
6. **GitHub Secrets** (Settings, Secrets and variables, Actions): `ANTHROPIC_API_KEY`, `IG_USER_ID`, `IG_ACCESS_TOKEN`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`.
7. **config.json** mein `competitors` mein 3-5 competitor accounts ke usernames likho (sirf Business/Creator accounts ka public data milta hai).

## Test pehle, live baad mein

- Actions tab, "Daily Instagram Autopilot", Run workflow, `dry_run = yes`. Telegram par preview image, caption aur report aayegi, par post nahi hogi.
- 2-3 din preview dekho. Sab sahi lage to live karne ke liye repo ki Settings, Variables mein `LIVE = 1` banao. Tab roz khud post hoga.
- Posting time badalne ke liye `.github/workflows/daily.yml` mein `cron` badlo (UTC time).

## Zaroori baatein

- Competitor/hashtag data ke liye Meta kabhi app review maangta hai. Agar data na mile to system general trends se post bana deta hai aur report mein "fallback" likhta hai.
- Hafte mein ek baar posts dekho. AI ke captions achhe hote hain, par aakhri quality check tumhari zimmedari hai.
- Claude API ka thoda kharch aata hai (roz 1 post ke liye bahut kam).
- Is project ko mene live APIs ke saath test nahi kiya. Isliye pehle dry run zaroor karo.
