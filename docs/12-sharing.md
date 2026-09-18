# 12 | Publish the learning, not the secrets

## Why a fresh teaching repository helps

A live server directory can contain credentials in places that are easy to
miss: environment files, generated JSON, database backups, shell history,
terminal recordings, request headers and copied troubleshooting output. A fresh
repository of examples is easier to review than a production export with a few
names blacked out.

This pack was built as a new teaching tree. It contains no imported production
Git history and no original screenshots. That reduces exposure, but it does
not establish a general guarantee about any future files you add.

## The publication checklist

Before sharing, check configuration, documentation, assets and repository
history. Replace actual addresses with fictional ones consistently. Remove
working credentials rather than substituting a weak shared class password.
Keep `.env.example`; exclude `.env`, generated data and private recovery files. Filled Xray/WireGuard profiles, client
subscription links and transport identity material also stay private.
Review tokenised download links and image metadata as well as visible text.

For future PDFs, drawing a black rectangle over text may leave the original
text, links or attachments in the file. Use real redaction or rebuild the
public document from sanitised source. Search its extracted text and inspect
its metadata and embedded links after export. For images, review the flattened
public export, not only the editing canvas. Do not publish a recovery QR code,
a blurred secret that remains legible, or a terminal title containing a private
machine identity.

A domain name is not normally a credential, but a collection of real service
names can map your infrastructure. This class pack uses fictional names because
the original addresses are unnecessary for understanding or reproducing it.
Do not mistake fictional names for an access-control mechanism on the live system.

## Create the GitHub repository without copying production history

Review the folder locally first. Then create a new empty repository in your own
GitHub account. Start private while reviewing it; change visibility deliberately
only after checking the intended audience and the material. No GitHub repository
was created or modified while this pack was prepared.

From the sanitised repository root:

```bash
git init -b main
git add README.md SECURITY.md CONTRIBUTING.md LICENSE .gitignore .gitattributes
git add SOURCES.md VALIDATION.md VERSION-RECORD.md
git add docs diagrams labs scripts tests tools pdf
git add MANIFEST.txt SHA256SUMS.txt
python3 scripts/check_publish.py
git diff --cached --stat
git diff --cached
```

The helper inspects staged blobs for a small set of credential patterns and
private-looking paths. It deliberately does not print matched secret values.
It is not a comprehensive secret scanner: it does not certify PDF/image contents,
all token formats, every address or the full Git history. Review the diff and
use additional secret-scanning controls appropriate to the repository.

Once the staged material has been reviewed:

```bash
git commit -m "Add sanitised classroom homelab projects"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

Replace both placeholders with the new repository you own. Use your existing
secure GitHub authentication method; never embed an access token in the remote
URL. Do not paste the example unchanged and expect it to create an account or
repository. A browser upload is also possible, but the same privacy review still
applies to every file selected.

## What if a secret was already committed?

Revoke or rotate it first. Deleting the visible file or adding it to `.gitignore`
does not remove it from old commits, forks, clones or downloaded releases.
Follow GitHub's sensitive-data-removal guidance and consider every location to
which the value was copied. Do not assume that rewriting history makes an
already-disclosed credential trustworthy again. [S21]

Do not commit the redaction map that links fictional names back to real ones.
Keep private test logs and operational version records separate unless their
contents have been reviewed for publication.

## Make the repository useful to another student

Start with a clear README, prerequisites, numbered steps, expected results,
troubleshooting and limitations. Keep commands in text rather than only in
screenshots. State where each command runs: laptop, lab server or controller.
Provide the selected image digests or release record when you have actually
built and verified them. A moving `latest` tag is not an immutable build record.

For future improvements, open an issue with a sanitised error description,
software versions, the failing step and a minimal reproduction. Do not attach
full diagnostic archives because they are convenient. Replace exact private
values without changing the technical relationship that explains the issue.

## Student evidence worksheet

Use a separate copy of the worksheet for each project. Fill in actual results.
Leave unperformed checks explicitly marked “not tested”.

| Field | Student record |
| --- | --- |
| Project and date | |
| Goal and permission/scope | |
| Host OS and selected release/image digests | |
| Data path and access-control design | |
| Why each major component is needed | |
| Positive test: command, expected result, actual result | |
| Negative test: command, expected result, actual result | |
| Persistence/recovery test | |
| Failure encountered and justified fix | |
| Limitations and untested cases | |
| Sensitive details removed before publication | |
| Sources, upstream attribution and assistance disclosure | |

Explain the work in your own understanding. This pack is not a set of assessment
answers and should not be represented as independently produced coursework
without following the relevant course rules.

**References:** S03, S21; repository SECURITY.md and VALIDATION.md.
