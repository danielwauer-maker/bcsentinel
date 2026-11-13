"""Read-only contract tests for opt-in daily systemd encrypted backups."""
import pathlib
import subprocess
import tempfile
import unittest

ROOT=pathlib.Path(__file__).resolve().parent

class BackupScheduleContractTests(unittest.TestCase):
    def test_shell_syntax(self):
        for file in ("offsite_backup.sh","scheduled_backup.sh","install_backup_timer.sh","backup_health.sh"):
            with self.subTest(file=file):
                p=subprocess.run(["bash","-n",str(ROOT/file)],text=True,capture_output=True)
                self.assertEqual(p.returncode,0,p.stderr)

    def test_explicit_activation_and_root_owned_copy(self):
        s=(ROOT/"install_backup_timer.sh").read_text()
        self.assertIn('--prepare',s)
        self.assertIn('--activate',s)
        self.assertIn('if [[ "$action" == "--activate" ]]',s)
        self.assertIn('systemctl enable --now',s)
        self.assertIn('install -o root -g root',s)
        self.assertIn("EnvironmentFile=/etc/bcsentinel-ai-backup/backup.env",s)
        self.assertIn("ProtectSystem=strict",s)
        self.assertIn("ReadWritePaths=/var/lib/bcsentinel-ai-backup",s)
        self.assertIn("CacheDirectory=bcsentinel-ai-backup",s)
        self.assertIn("RCLONE_CACHE_DIR=",s)
        self.assertIn("OnCalendar=*-*-* 03:20:00 UTC",s)
        self.assertIn("Persistent=true",s)
        self.assertIn("flock -n",s)
        self.assertNotIn("restic forget",s)
        self.assertNotIn("restic prune",s)

    def test_wrapper_stores_status_and_never_prunes(self):
        s=(ROOT/"scheduled_backup.sh").read_text()
        self.assertIn("last-success",s)
        self.assertIn("last-failure",s)
        self.assertIn("trap on_exit EXIT",s)
        self.assertIn('bash "$ROOT/offsite_backup.sh"',s)
        for forbidden in ("restic forget","restic prune","systemctl enable","docker compose","rm -rf /"):
            self.assertNotIn(forbidden,s)

    def test_health_fails_closed_when_unconfigured(self):
        p=subprocess.run(["bash",str(ROOT/"backup_health.sh")],capture_output=True,text=True)
        self.assertNotEqual(p.returncode,0)
        self.assertIn("BACKUP_HEALTH_FAIL",p.stdout)

    def test_install_does_not_run_without_opt_in(self):
        p=subprocess.run(["bash",str(ROOT/"install_backup_timer.sh")],
                         capture_output=True,text=True)
        self.assertNotEqual(p.returncode,0)
        self.assertIn("Usage:",p.stderr) if "Usage:" in p.stderr else self.assertIn("root",p.stderr)

if __name__=="__main__": unittest.main()
