# Research Progress

**STATUS: COMPLETE.** All unique organisations from the original 748-row legacy list have
been fully researched to V5 depth. Final unique count settled at 708 (not the earlier 727
estimate) as additional in-list duplicates and near-duplicate seed rows were identified and
merged during research — see `scripts/next_batch.py` `MANUAL_ALIASES` for the full list of
manually-resolved aliases beyond what the mechanical dedup logic could catch on its own.

- Full V5 profile complete (markdown + sourced + confidence-rated + schema-v2 CSV row): 708
- Remaining: 0

Note: from org #398 onward (~Looping/M-names onward), profiles use a leaner format at the
user's request to increase throughput: 1-2 sources per org instead of 2-4, ~50-word overview/
~75-word business model instead of 100/150-200, terser bullet-style sections, 1-2 line
Verification Notes. The "never invent, mark unconfirmed as Not publicly available" rule is
unchanged - only prose depth and source-count were reduced, not verification rigor.

Note: 4 completed profiles (Coca-Cola Returnables, Flo Hygiene, Bio-Home, For Earth's Sake) have corrected
names/spellings vs. the original legacy list (which had typos/wrong countries) — tracked here by their
corrected slug, not the original list's exact string.

Schema: `data/REUSE_V5_Master.csv` uses the expanded 34-column V5 schema (adds GitHub slug, short summary,
logo/featured image URL, SEO description, primary colour, tags, last verified/updated dates, researcher,
source count, overall confidence score, REUSE priority rating, SDGs — see README for full method).
Generated mechanically from each org's markdown profile via `scripts/parse_md_to_csv.py` — free to re-run,
no API calls needed, so CSV regeneration never costs research budget.

## Priority batch research log (all complete)

- [x] L'Occitane — global brand; PH listing is a retail market, not a distinct subsidiary; see organisations/l-occitane.md
- [x] Akomeya — see organisations/akomeya.md
- [x] Alima Pure — CEASED (~2025); country corrected US not Canada; see organisations/alima-pure.md
- [x] Allas — Indonesia; NGO-incubated venture (Enviu/Zero Waste Living Lab); see organisations/allas.md
- [x] Almang Market — see organisations/almang-market.md
- [x] Bio C' Bon — Japan; joint venture Aeon/Marne & Finance; see organisations/bio-c-bon.md
- [x] Bio-Home — Singapore; brand of Lam Soon; see organisations/bio-home.md
- [x] Coca-Cola Returnables — Brazil; multi-bottler packaging program, not a standalone company; see organisations/coca-cola-returnables.md
- [x] ECCBC / UNIDO PET pilot — Morocco; recycling/material-recovery pilot, not a reuse programme; see organisations/eccbc-unido-pet-pilot.md
- [x] EcoNowCA — US; active but consolidating locations; see organisations/econowca.md
- [x] Ernie's Zero Waste Shop — UK; independent refill shop, founded 2019; see organisations/ernies-zero-waste-shop.md
- [x] Evy Café — Switzerland; sparse/no verified reuse activity found; see organisations/evy-cafe.md
- [x] Flo Hygiene — Nepal; parent co. TNT Hygiene; see organisations/flo-hygiene.md
- [x] For Earth's Sake — country corrected UK not India; see organisations/for-earths-sake.md
- [x] Green Joy — Vietnam; materials-substitution manufacturer, not core reuse; see organisations/green-joy.md
- [x] Green Upshot — see organisations/green-upshot.md
- [x] Hoa Đất – Tiêu dùng an lành — see organisations/hoa-dat-tieu-dung-an-lanh.md
- [x] HRK Group — see organisations/hrk-group.md
- [x] KinkoCare — see organisations/kinkocare.md
- [x] Let's Get Naked Refill — see organisations/lets-get-naked-refill.md
- [x] Maria Granel — see organisations/maria-granel.md
- [x] Mi Barrio Sin Residuos (UNDP project) — see organisations/mi-barrio-sin-residuos.md
- [x] miniml — see organisations/miniml.md
- [x] Moon Berry Made — see organisations/moon-berry-made.md
- [x] Mottainai Refill — 3 duplicate seed rows, one profile; see organisations/mottainai-refill.md
- [x] My Naked Bar — see organisations/my-naked-bar.md
- [x] MyEarth — actually L'earth (S) Pte Ltd, Singapore; bio-composite single-use, low relevance; see organisations/myearth.md
- [x] mymizu — Japan + Philippines chapter (Mymizu PH); see organisations/mymizu.md, organisations/mymizu-ph.md
- [x] Nashonuma — see organisations/nashonuma.md
- [x] Net Zero Co. — see organisations/net-zero-co.md
- [x] O Granel da Sofia — see organisations/o-granel-da-sofia.md
- [x] Ong Hut Co — Vietnam; single-use biodegradable straws, not reuse; see organisations/ong-hut-co.md
- [x] Ozarka — Netherlands; site is live (seed's "broken" note was wrong); see organisations/ozarka.md
- [x] Packaging Cluster / Green Impackt — lead org is Spain-based, Green Impackt is EU-funded Colombia programme; see organisations/packaging-cluster-green-impackt.md
- [x] Pakpet — Pakistan; no dedicated reuse/refill line found, low-confidence inclusion; see organisations/pakpet.md
- [x] Paraguay Sin Basura (“Reduce” guide) — see organisations/paraguay-sin-basura.md
- [x] Pfaffhüsli — see organisations/pfaffhusli.md
- [x] Pizza 4P’s — see organisations/pizza-4ps.md
- [x] PolyLayerTech — see organisations/polylayertech.md
- [x] Rampe5 ZeroWaste Ladencafé — Zurich; see organisations/rampe5-zerowaste-ladencafe.md
- [x] Re-up Refill — merged w/ duplicate seed row "Re up Refills"; see organisations/re-up-refills.md
- [x] Recicla y Reusa Venezuela — no matching org confirmed publicly; thin profile per rules; see organisations/recicla-y-reusa-venezuela.md
- [x] Reciclaje Moreno (AIM2Flourish) — no matching org confirmed publicly; thin profile per rules; see organisations/reciclaje-moreno-aim2flourish.md
- [x] Reciclarte — no matching org confirmed publicly; thin profile per rules; see organisations/reciclarte.md
- [x] rĒCo Refillery — matches organisations/reco.md (Reco, UK)
- [x] Refill — generic legacy seed entry, resolved via fuzzy-match against existing refill-named profiles
- [x] Refill H2O – IPVC — Portugal; university IoT refill pilot; see organisations/refill-h2o-ipvc.md
- [x] Refiller Mobile — Malaysia; see organisations/refiller-mobile.md
- [x] Replenish Refillery & Zero Waste Store — Canada; confirmed independent of the similarly-named US company; see organisations/replenish-refillery-canada.md
- [x] Reuso.io — US; see organisations/reuso-io.md
- [x] Sanima — see organisations/sanima.md
- [x] Sankoty Sustainables — see organisations/sankoty-sustainables.md
- [x] Saponetti — merged w/ duplicate seed row "Saponetti Soaps"; see organisations/saponetti.md
- [x] Saponetti Soaps — merged into organisations/saponetti.md
- [x] Savonnerie des Diligences — see organisations/savonnerie-des-diligences.md
- [x] Searious Business – MOSSUP — Morocco pilot; see organisations/searious-business-mossup.md
- [x] Seeker's spirits — see organisations/seekers-spirits.md
- [x] Shuangti — see organisations/shuangti.md
- [x] Slo Store — see organisations/slo-store.md
- [x] SmartFilter — see organisations/smartfilter.md
- [x] SOCSE — see organisations/socse.md
- [x] Solid — see organisations/solid-oral-care.md
- [x] Sonora Reffilery — actual name Sonora Refillery; see organisations/sonora-reffilery.md
- [x] Spruce Refill — merged w/ duplicate seed row "Spruce"; see organisations/spruce.md
- [x] Sun Moon Rain — see organisations/sun-moon-rain.md
- [x] Sunrise Straws — actual name Sunbird Straws; see organisations/sunbird-straws.md
- [x] Sunsilk — Unilever refill programme, Pakistan; see organisations/sunsilk-pakistan-refill.md
- [x] Sustenir — seed miscategorised; actually a vertical-farming co, no reuse activity; see organisations/sustenir.md
- [x] Tạp Hóa Lá Xanh — see organisations/tap-hoa-la-xanh.md
- [x] Tarım Kredi Sıfır Market — see organisations/tarim-kredi-sifir-market.md
- [x] Tetra Pak Paraguay — see organisations/tetra-pak-paraguay.md
- [x] The Ditty Bag — see organisations/the-ditty-bag.md
- [x] The Green Bee — see organisations/the-green-bee.md
- [x] The Mayan Collective — see organisations/the-mayan-collective.md
- [x] The Nature Masons — uses tin not aluminium containers, corrected; see organisations/the-nature-masons.md
- [x] The Purest Solutions — see organisations/the-purest-solutions.md
- [x] The Refillary Storehouse — actual name/location: The Refillery Storehouse, Poughkeepsie NY (not Canada); see organisations/the-refillery-storehouse.md
- [x] The Sustainability Project — see organisations/the-sustainability-project.md
- [x] The Tare Market — see organisations/the-tare-market.md
- [x] The Unwaste Shop — see organisations/the-unwaste-shop.md
- [x] The Wallet Shop — see organisations/the-wallet-shop.md
- [x] The Wally Shop — see organisations/the-wally-shop.md
- [x] The Waste Free Co. — see organisations/the-waste-free-co.md
- [x] Tip Toe Eco Marketplace — see organisations/tip-toe-eco-marketplace.md
- [x] TNT Bags — see organisations/tnt-bags.md
- [x] Touch the Toes — see organisations/touch-the-toes.md
- [x] TRAMUCO (via COOPI initiative) — full name Transformación, Mujeres, Comunidad; see organisations/tramuco-coopi.md
- [x] Trash Hero Czech Republic — see organisations/trash-hero-czech-republic.md
- [x] Trashit — see organisations/trashit.md
- [x] Unibag — country corrected Chile not Peru; see organisations/unibag.md
- [x] Unilever Colombia (FAB, Dirt is Good) — home-care business sold to Alicorp Jan 2026, ownership corrected; see organisations/unilever-colombia-fab-dirt-is-good.md
- [x] Unit Goods — existence could not be verified; thin stub; see organisations/unit-goods.md
- [x] Unpackaged Eco (potentially closed?) — no closure evidence found, appears active; see organisations/unpackaged-eco.md
- [x] V's HOME – Veggie Restaurant & Café — Vietnam; appears closed per 2022 review; see organisations/vs-home-veggie-restaurant-cafe.md
- [x] Venezolana de Reciclaje, C.A. — see organisations/venezolana-de-reciclaje.md
- [x] Venezuela Refill Initiative — domain does not resolve, unverifiable; see organisations/venezuela-refill-initiative.md
- [x] VerdeMar — conventional supermarket chain w/ no-plastic-bag policy, not reuse-centric; see organisations/verdemar.md
- [x] Vermont Soap — duplicate of The Castile Soap Shop (same contact/company); see organisations/the-castile-soap-shop.md
- [x] Village General Store — see organisations/village-general-store.md
- [x] Wasteupso Zero-Waste Shop — see organisations/wasteupso-zero-waste-shop.md
- [x] Well Spent Grain — see organisations/well-spent-grain.md
- [x] Wheedle — see organisations/wheedle.md
- [x] Woosh Water — see organisations/woosh-water.md
- [x] XICLO / Biocírculo — seed conflated two distinct companies; both researched separately; see organisations/xiclo.md, organisations/xiclo-biocirculo.md
- [x] XXL Refill — see organisations/xxl-refill.md
- [x] Your Sustainable store — see organisations/your-sustainable-store.md
- [x] Zero Waste Harare (women-led) — informal group, no dedicated website; see organisations/zero-waste-harare.md
- [x] Zero Waste Reserve — see organisations/zero-waste-reserve.md
- [x] Zero Waste Store NL — website 404'd, social-media presence only; see organisations/zero-waste-store-nl.md
- [x] Zeropolitan — country corrected Australia not Pakistan; see organisations/zeropolitan.md
- [x] Zerosporo — actual name Zero Posro; see organisations/zeroposro.md
