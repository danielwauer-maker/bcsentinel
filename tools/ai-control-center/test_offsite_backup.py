"""AI-PM 2.1 remote-backup guard tests. No remote repo or secret is used."""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT=Path(__file__).parent/"offsite_backup.sh"

class OffsiteBackupContractTests(unittest.TestCase):
    def test_bash_syntax(self):
        p=subprocess.run(["bash","-n",str(SCRIPT)],capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr)

    def test_denies_non_root_before_any_backup_activity(self):
        if os.geteuid()==0:
            self.skipTest("Root CI cannot test non-root restriction")
        p=subprocess.run(["bash",str(SCRIPT)],capture_output=True,text=True,
                         env={"PATH":os.environ.get("PATH",""),"HOME":"/tmp"})
        self.assertNotEqual(p.returncode,0)
        self.assertIn("root",p.stderr)

    def test_script_is_explicit_and_fails_closed(self):
        text=SCRIPT.read_text()
        for required in (
            "RESTIC_REPOSITORY","RESTIC_PASSWORD_FILE",
            '[[ "\${EUID}" -eq 0 ]]', "restic cat config",
            "sftp:*|s3:*|b2:*|rclone:*|rest:https://*",
            "backup_verify.py", "restore latest", "restic check",
            "OFFSITE_BACKUP_AND_RESTORE_PASS","trap cleanup EXIT"):
            with self.subTest(required=required):
                self.assertIn(required.replace("\\",""),text)
        for unsafe in ("restic init","restic forget","restic prune","chmod -R",
                       "chown -R","docker compose down","git push"):
            self.assertNotIn(unsafe,text)

    def test_no_credential_files_committed(self):
        root=Path(__file__).parent
        for filename in (".restic-password","restic-password","offsite.env"):
            self.assertFalse((root/filename).exists())

if __name__=="__main__":unittest.main()
