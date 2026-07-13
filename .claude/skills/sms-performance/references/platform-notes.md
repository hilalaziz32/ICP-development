# GoHighLevel API — the landmines

Every one of these cost real time to find. `tools/ghl_mine.py` already handles all of them —
this file exists so you don't "helpfully" undo one, and so a fresh session doesn't rediscover
them the hard way.

## Auth & setup

| | |
|---|---|
| MCP endpoint | `https://services.leadconnectorhq.com/mcp/anthropic/v2` (HTTP, stateless) |
| Auth | `Authorization: Bearer pit-…` only. No `locationId` header needed. |
| Token scope | A Private Integration Token is **per sub-account**, created in *Settings → Private Integrations*. One MCP server per client: `ghl-<client>`. |
| Scopes | Grant every `readonly` scope. **Never** grant `conversations/message.write` — it lets an agent send real SMS to live prospects. |
| REST `Version` header | Required. `2021-04-15` for conversations, `2021-07-28` for contacts/locations. |

## The landmines

**1. `locationId` is required but NOT auto-injected.**
Nearly every operation needs `locationId` as a **query param**. The MCP does not add it — a
`dryRun` shows an empty query, and the call fails with a misleading
`403 "The token does not have access to this location."` The token is fine. Pass `locationId`.

**2. GHL's WAF 403s Python's default User-Agent.**
`urllib` sends `Python-urllib/3.x` and gets blocked. Set any normal UA (`curl/8.7.1`) or use curl.
The same request works from curl and fails from Python — this looks like an auth bug and isn't.

**3. Don't use the MCP for bulk pulls — use direct REST.**
`execute_operation` times out on the **2nd cursor page** (`401 "Command timed out"`) and caps
contacts at 100/page. Direct REST with the same PIT is faster and doesn't break. The MCP is for
interactive questions; the miner is for volume.

**4. Contacts hard-cap at 10,000 via page numbers.**
`POST /contacts/search` with `page` silently stops at 10k. You must deep-paginate with the
`searchAfter` array found on the **last contact of each page**. Direct REST also allows
`pageLimit: 500` (the MCP caps it at 100).

**5. Message export: `limit` must be ≥ 10**, else `422`. Max 1000.

**6. Cursor pagination on messages is sequential and slow (~5s/call).**
158k messages = ~14 min single-threaded. Split into **monthly `startDate`/`endDate` windows**
and pull them in parallel (8 workers → ~3.5 min). Dedupe on message `id` at the window edges.

**7. Custom-field IDs are DIFFERENT per sub-account.**
`competitor_1` has one ID in Digital Resource and a different one in Kynship. **Resolve by
`fieldKey`** (`contact.competitor_1`) via `GET /locations/{id}/customFields`. Hardcoding IDs
does not error — it silently fails to de-merge, and you get garbage that looks plausible.

**8. Sub-accounts get reused between clients.**
See rule 3 in SKILL.md. Always scope to the client's era.

## Where the data actually lives

| Want | Endpoint | Notes |
|---|---|---|
| Campaign names | `GET /workflows/` | name, status, dates — **no message content, ever** |
| **The SMS copy** | `GET /conversations/messages/export` | `body`, `direction`, `status` (incl. `opt_out`), `contactId` |
| Campaign attribution | `POST /contacts/search` | the contact's `contact.workflow_name` / `workflow_id` custom fields |
| Merge values (to de-merge) | same contact record | `firstName`, `city`, `competitor_1/2`, `case_study_1/2`, `ai_first_line`, … |

`contact.ai_first_line` is an **AI-written opener unique to every prospect**. Fail to strip it
and every single message looks like a distinct copy variant — you'd report thousands of
"variants" that are really one template.
