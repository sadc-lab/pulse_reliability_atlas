# Shared rule: which paths must never enter this repository's history.
# Sourced by .githooks/pre-commit (first barrier) and .githooks/pre-push
# (second barrier, which also catches a `git commit --no-verify`).
#
# Why (2026-10-07). The guard used to list reviewer files by their exact names
# (an annotated PDF, revised Word files, each named after its reviewer). Every
# new review round arrives under a new name, so the next supervisor's file
# would have passed. The rules below do not depend on names:
#
#   1. anything under retours_chefs/  -- the one place to drop reviewers'
#      returns (the folder is also in .gitignore);
#   2. any word-processor document (.doc, .docx, .odt, .rtf, .pages) anywhere:
#      the repository tracks none (measured 2026-10-07: 0 in `git ls-files`);
#      the Word twins of the paper live in the gitignored preprint_npj/build/;
#   3. any PDF outside the folders that legitimately hold figures and the
#      journal template (figures/, preprint_npj/figures/, preprint_npj/template/):
#      supervisors also return annotated PDFs;
#   4. the internal notes the guard already covered (TODO_*, ROADMAP_*,
#      NEXT_SESSION*, internal_morris_rebuttal.md).
#
# Broad on purpose: this guard fails LOUDLY (the commit or push stops and says
# why), unlike .gitignore, which must stay literal. If a file caught here is
# genuinely meant to be public, change these rules deliberately and say why in
# the commit message.

SENSITIVE_RE='(^|/)retours_chefs/|\.(docx?|odt|rtf|pages)$|(^|/)TODO_[^/]*\.md$|(^|/)ROADMAP_[^/]*\.md$|(^|/)NEXT_SESSION[^/]*\.md$|(^|/)internal_morris_rebuttal\.md$'
PDF_ALLOWED_RE='^(figures|preprint_npj/figures|preprint_npj/template)/'

# stdin: one repository-relative path per line; stdout: the paths that must not
# be committed or pushed.
sensitive_paths() {
    while IFS= read -r path; do
        [ -z "$path" ] && continue
        if printf '%s\n' "$path" | grep -Eqi "$SENSITIVE_RE"; then
            printf '%s\n' "$path"
            continue
        fi
        case "$path" in
            *.[pP][dD][fF])
                printf '%s\n' "$path" | grep -Eq "$PDF_ALLOWED_RE" || printf '%s\n' "$path"
                ;;
        esac
    done
}
