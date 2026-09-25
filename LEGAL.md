# JANISSARY — Terms of Use

**Version 1 — effective 2026-09-25**

JANISSARY is a dual-use security testing tool. It is intended for use
only against systems you own, or systems you have the prior, explicit,
written permission of the owner to test.

These Terms supplement the [Apache License 2.0](LICENSE) that governs
the source code. They do not replace or modify it. Where these Terms
and the Apache License 2.0 conflict on a matter of *use* (as opposed
to a matter of *copyright licensing*), these Terms govern.

By running any network command — `scan`, `fingerprint`, `graphql`,
`ws`, `admin`, or `attack` — you accept these Terms. Acceptance is
recorded locally in `~/.janissary/terms-accepted.json`. No data is
transmitted anywhere.

---

## 1. Authorised use

You must not use JANISSARY to access, scan, probe, extract data from,
or interfere with any system, network, or data unless you have the
prior, explicit, written authorisation of the system owner.

**Australia.** Unauthorised access to restricted data is an offence
under s 478.1 of the *Criminal Code Act 1995* (Cth), carrying up to
2 years' imprisonment. Aggravated offences under ss 477.1–477.3 carry
up to 10 years. Producing or supplying software with the intention
that it be used to commit a computer offence is itself an offence
under s 478.4, carrying up to 5 years.

**United States.** Unauthorised access to a protected computer is an
offence under 18 U.S.C. § 1030 (Computer Fraud and Abuse Act), with
both civil and criminal penalties. *Van Buren v. United States* (2021)
narrowed "exceeds authorized access" but did not change the
requirement of authorisation.

**Other jurisdictions.** Equivalent offences exist in the United
Kingdom (Computer Misuse Act 1990), the European Union (Directive
2013/40/EU), Canada (Criminal Code s 342.1), and most other
jurisdictions. It is your responsibility to know and comply with the
law that applies to you.

---

## 2. Indemnity

You agree to indemnify, defend, and hold harmless the developer,
contributors, and copyright holders of JANISSARY (each an
**Indemnified Party**) from and against any and all claims, demands,
actions, suits, losses, liabilities, damages, costs, and expenses
(including reasonable legal fees) arising out of or in connection
with:

  (a) your use of JANISSARY;
  (b) your breach of clause 1 of these Terms;
  (c) your unauthorised access to any system, network, or data; or
  (d) any modification you make to JANISSARY.

This indemnity does not extend to claims arising from the wilful
misconduct or gross negligence of the Indemnified Party.

---

## 3. Limitation of liability

To the maximum extent permitted by law, the developer, contributors,
and copyright holders of JANISSARY will not be liable for any damages
arising from the use or inability to use JANISSARY, whether in
contract, tort (including negligence), statute, or otherwise.

Where liability cannot be excluded but may be limited, total aggregate
liability is limited to the amount you paid for JANISSARY, which for
this open-source distribution is **zero (AUD 0.00)**.

Nothing in this clause excludes liability that cannot lawfully be
excluded, including under the *Australian Consumer Law* where
applicable.

---

## 4. Export control and sanctions

JANISSARY may be subject to export control and sanctions laws,
including Australia's *Defence and Strategic Goods List* (DSGL),
administered by the Defence Export Controls office, and the United
States *Export Administration Regulations* (EAR).

You must not use, export, re-export, or transfer JANISSARY in
violation of those laws, or to any person or entity subject to
Australian autonomous sanctions, UN Security Council sanctions, or
United States sanctions administered by OFAC.

Publishing JANISSARY on a public repository constitutes an export to
every jurisdiction with internet access. If you intend to distribute
JANISSARY, you are responsible for confirming your own compliance
with the DSGL and applicable sanctions regimes.

---

## 5. Good-faith research

JANISSARY is designed for good-faith security testing and research.

Use it only in a way that avoids harm to individuals and the public.
Use the information it produces primarily to improve the security of
the affected systems. Do not use it to extract, retain, or disclose
data you are not authorised to access.

This clause tracks the three-part good-faith definition in the United
States Department of Justice's CFAA charging policy (May 2022).

---

## 6. No warranty

JANISSARY is provided "as is", without warranty of any kind, as set
out in section 7 of the Apache License 2.0.

---

## 7. Governing law and jurisdiction

These Terms are governed by the laws of **Victoria, Australia**. The
parties submit to the exclusive jurisdiction of the courts of
**Victoria, Australia**.

---

## 8. Acceptance

Acceptance can be recorded in any of the following ways:

- Running any gated command (`scan`, `fingerprint`, `graphql`, `ws`,
  `admin`, `attack`) and typing `I AGREE` at the prompt.
- Running `janissary terms accept`.
- Setting the environment variable `JANISSARY_ACCEPT_TERMS=1` for the
  duration of a process (useful in CI, Docker, and provisioning
  scripts).

The acceptance record contains only a version number and a UTC
timestamp. It contains no personal information and is never
transmitted.

To review the full text at any time:

    janissary terms show

To check whether acceptance is current:

    janissary terms status

---

## 9. Limitation of these Terms

These Terms apply to the CLI entry point. A user who imports
`janissary` as a Python library, or who modifies the source, may
bypass the acceptance gate. That does not waive these Terms; it means
the acceptance record does not exist for that user. The authorised-use
requirement, the indemnity, and the limitation of liability apply to
all use of JANISSARY regardless of how it is invoked.
