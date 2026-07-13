# references/ — this skill reads the shared SMS playbook

mechanism-wordsmith does **not** keep its own copy of patterns/voice/winners. To stay consistent with
sms-draft and the rest of the system, it reads the single shared playbook at the repo root:

- `sms-playbook/Cold-SMS-Voice-Profile-Scaletopia.md` — tonal source of truth (banlist, closer-test, native-unit, picture>label, casing/CTA)
- `sms-playbook/winners.csv` — the 17 tagged winners = the **routing source** (match case → closest winner → lever/pattern/what-carries/omit-or-generate)
- `sms-playbook/pattern-library.md` — two-tier model + mechanism patterns + connectors
- `sms-playbook/FUNDAMENTALS.md` — the spine
- `sms-playbook/levers.md` — light support (5 psychological levers)

> At package time (for distribution as a `.skill`), copy these files in here so the bundle is
> self-contained. While running in this repo, read them by their `sms-playbook/...` paths.
