# Release candidate integrity

The original `SEMS_Final_Academic_Professional_Release_v2.zip` is the verified v2 source package. It is intentionally **not** committed to ordinary Git history. Its expected SHA-256 is recorded in [the checksum manifest](SEMS_Final_Academic_Professional_Release_v2.zip.sha256). The repository may also contain later MatCount-specific documentation, workflow and governance files; those additions do not retroactively alter the original archive or its digest.

The 2026-10-04 audit found critical/high runtime advisories in that original ZIP. Keep it privately as provenance; **do not attach it as the patched prerelease**. The corrected source candidate is named `MatCount_SEMS_v2_Academic_Release_Candidate_RC1.zip`, with a separate `.sha256` asset and a repository checksum manifest generated only after the immutable ZIP bytes are final. See the [security remediation record](../docs/SECURITY_REMEDIATION_2026-10-04.md).

From the repository root, after downloading either named archive and its matching checksum asset:

```powershell
python scripts/verify_release_artifacts.py --archive .\MatCount_SEMS_v2_Academic_Release_Candidate_RC1.zip
```

On Unix-like systems, substitute `./MatCount_SEMS_v2_Academic_Release_Candidate_RC1.zip`. The verifier checks the matching committed manifest, SHA-256, ZIP readability, safe member names, duplicate paths, suspicious file types and excluded private/generated paths. It never extracts or modifies the archive. If the ZIP is unavailable, `python scripts/verify_release_artifacts.py` checks manifest format and staging tree only; that is **not** a substitute for archive verification.

After upload, download the candidate asset afresh, rerun the verifier and confirm its tag points to the reviewed commit. A clean extraction may omit the candidate's own checksum to avoid the self-hashing impossibility; pass `--manifest` with the separately downloaded `.sha256` file if verifying there. Do not promote to final until the Windows/MySQL/Workbench and human acceptance tasks are complete. Preserve the original v2 and private rollback artifacts separately.
