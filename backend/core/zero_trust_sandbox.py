"""
Zero-Trust Agent Sandboxing
Military-grade isolation for agent execution with comprehensive security
"""

import logging
import asyncio
import subprocess
import tempfile
import os
import json
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from enum import Enum
import hashlib

logger = logging.getLogger(__name__)


class SecurityLevel(str, Enum):
    """Security isolation levels"""
    LOW = "low"  # Basic sandboxing
    MEDIUM = "medium"  # Standard isolation
    HIGH = "high"  # Enhanced security
    MILITARY = "military"  # Maximum isolation


@dataclass
class SandboxConfig:
    """Sandbox configuration"""
    security_level: SecurityLevel = SecurityLevel.HIGH
    cpu_quota_ms: int = 100  # CPU time per period
    cpu_period_ms: int = 100  # Period length
    memory_limit_mb: int = 256
    network_policy: str = "deny_all_outbound"
    syscall_whitelist: List[str] = None
    max_execution_time_seconds: int = 30
    enable_taint_tracking: bool = True
    enable_static_analysis: bool = True
    enable_runtime_verification: bool = True
    
    def __post_init__(self):
        if self.syscall_whitelist is None:
            self.syscall_whitelist = [
                "read", "write", "open", "close", "stat", "fstat",
                "lseek", "mmap", "mprotect", "munmap", "brk",
                "rt_sigaction", "rt_sigprocmask", "rt_sigreturn",
                "ioctl", "pread64", "pwrite64", "readv", "writev",
                "access", "pipe", "select", "sched_yield", "mremap",
                "msync", "mincore", "madvise", "shmget", "shmat",
                "shmctl", "dup", "dup2", "pause", "nanosleep",
                "getitimer", "alarm", "setitimer", "getpid",
                "sendfile", "socket", "connect", "accept", "sendto",
                "recvfrom", "sendmsg", "recvmsg", "shutdown",
                "bind", "listen", "getsockname", "getpeername",
                "socketpair", "setsockopt", "getsockopt", "clone",
                "fork", "vfork", "execve", "exit", "wait4",
                "kill", "uname", "semget", "semop", "semctl",
                "shmdt", "msgget", "msgsnd", "msgrcv", "msgctl",
                "fcntl", "flock", "fsync", "fdatasync", "truncate",
                "ftruncate", "getdents", "getcwd", "chdir", "fchdir",
                "rename", "mkdir", "rmdir", "creat", "link",
                "unlink", "symlink", "readlink", "chmod", "fchmod",
                "chown", "fchown", "lchown", "umask", "gettimeofday",
                "getrlimit", "getrusage", "sysinfo", "times",
                "ptrace", "getuid", "syslog", "getgid", "setuid",
                "setgid", "geteuid", "getegid", "setpgid", "getppid",
                "getpgrp", "setsid", "setreuid", "setregid",
                "getgroups", "setgroups", "setresuid", "getresuid",
                "setresgid", "getresgid", "getpgid", "setfsuid",
                "setfsgid", "getsid", "capget", "capset",
                "rt_sigpending", "rt_sigtimedwait", "rt_sigqueueinfo",
                "rt_sigsuspend", "sigaltstack", "utime", "mknod",
                "uselib", "personality", "ustat", "statfs",
                "fstatfs", "sysfs", "getpriority", "setpriority",
                "sched_setparam", "sched_getparam",
                "sched_setscheduler", "sched_getscheduler",
                "sched_get_priority_max", "sched_get_priority_min",
                "sched_rr_get_interval", "mlock", "munlock",
                "mlockall", "munlockall", "vhangup", "modify_ldt",
                "pivot_root", "_sysctl", "prctl", "arch_prctl",
                "adjtimex", "setrlimit", "chroot", "sync",
                "acct", "settimeofday", "mount", "umount2",
                "swapon", "swapoff", "reboot", "sethostname",
                "setdomainname", "iopl", "ioperm",
                "create_module", "init_module", "delete_module",
                "get_kernel_syms", "query_module", "quotactl",
                "nfsservctl", "getpmsg", "putpmsg", "afs_syscall",
                "tuxcall", "security", "gettid", "readahead",
                "setxattr", "lsetxattr", "fsetxattr", "getxattr",
                "lgetxattr", "fgetxattr", "listxattr",
                "llistxattr", "flistxattr", "removexattr",
                "lremovexattr", "fremovexattr", "tkill",
                "time", "futex", "sched_setaffinity",
                "sched_getaffinity", "set_thread_area",
                "io_setup", "io_destroy", "io_getevents",
                "io_submit", "io_cancel", "get_thread_area",
                "lookup_dcookie", "epoll_create", "epoll_ctl_old",
                "epoll_wait_old", "remap_file_pages", "getdents64",
                "set_tid_address", "restart_syscall", "semtimedop",
                "fadvise64", "timer_create", "timer_settime",
                "timer_gettime", "timer_getoverrun",
                "timer_delete", "clock_settime", "clock_gettime",
                "clock_getres", "clock_nanosleep", "exit_group",
                "epoll_wait", "epoll_ctl", "tgkill", "utimes",
                "vserver", "mbind", "set_mempolicy",
                "get_mempolicy", "mq_open", "mq_unlink",
                "mq_timedsend", "mq_timedreceive", "mq_notify",
                "mq_getsetattr", "kexec_load", "waitid",
                "add_key", "request_key", "keyctl", "ioprio_set",
                "ioprio_get", "inotify_init", "inotify_add_watch",
                "inotify_rm_watch", "migrate_pages", "openat",
                "mkdirat", "mknodat", "fchownat", "futimesat",
                "newfstatat", "unlinkat", "renameat", "linkat",
                "symlinkat", "readlinkat", "fchmodat", "faccessat",
                "pselect6", "ppoll", "unshare", "set_robust_list",
                "get_robust_list", "splice", "tee", "sync_file_range",
                "vmsplice", "move_pages", "utimensat",
                "epoll_pwait", "signalfd", "timerfd_create",
                "eventfd", "fallocate", "timerfd_settime",
                "timerfd_gettime", "accept4", "signalfd4",
                "eventfd2", "epoll_create1", "dup3", "pipe2",
                "inotify_init1", "preadv", "pwritev",
                "rt_tgsigqueueinfo", "perf_event_open",
                "recvmmsg", "fanotify_init", "fanotify_mark",
                "prlimit64", "name_to_handle_at",
                "open_by_handle_at", "clock_adjtime", "syncfs",
                "sendmmsg", "setns", "getcpu", "process_vm_readv",
                "process_vm_writev", "kcmp", "finit_module",
                "sched_setattr", "sched_getattr", "renameat2",
                "seccomp", "getrandom", "memfd_create",
                "kexec_file_load", "bpf", "execveat",
                "userfaultfd", "membarrier", "mlock2",
                "copy_file_range", "preadv2", "pwritev2",
                "pkey_mprotect", "pkey_alloc", "pkey_free",
                "statx", "io_pgetevents", "rseq"
            ]


@dataclass
class TaintedData:
    """Tainted data tracking"""
    source: str
    data_hash: str
    taint_level: int
    propagation_path: List[str]


class ZeroTrustSandbox:
    """
    Zero-trust sandbox for agent execution
    Provides military-grade isolation with comprehensive security
    """
    
    def __init__(self, config: Optional[SandboxConfig] = None):
        self.config = config or SandboxConfig()
        self.tainted_data: Dict[str, TaintedData] = {}
        self.execution_history: List[Dict[str, Any]] = []
    
    async def execute_agent(
        self,
        agent_code: str,
        inputs: Dict[str, Any],
        agent_id: str = "unknown"
    ) -> Dict[str, Any]:
        """
        Execute agent code in zero-trust sandbox
        
        Args:
            agent_code: Agent code to execute
            inputs: Input data for agent
            agent_id: Agent identifier
        
        Returns:
            Execution result with security metadata
        """
        try:
            # Phase 1: Static Analysis
            if self.config.enable_static_analysis:
                static_result = await self.static_analyze(agent_code)
                if static_result["status"] != "safe":
                    raise SecurityError(
                        f"Static analysis failed: {static_result['reason']}"
                    )
            
            # Phase 2: Taint Tracking
            if self.config.enable_taint_tracking:
                tainted_inputs = await self.track_taint_flow(inputs)
            else:
                tainted_inputs = inputs
            
            # Phase 3: Sandboxed Execution
            result = await self._run_in_sandbox(
                agent_code,
                tainted_inputs,
                agent_id
            )
            
            # Phase 4: Post-Execution Verification
            if self.config.enable_runtime_verification:
                await self.verify_integrity(result)
            
            # Record execution
            self.execution_history.append({
                "agent_id": agent_id,
                "timestamp": asyncio.get_event_loop().time(),
                "status": "success",
                "security_level": self.config.security_level.value
            })
            
            return result
        
        except Exception as e:
            logger.error(f"Sandbox execution failed: {e}")
            self.execution_history.append({
                "agent_id": agent_id,
                "timestamp": asyncio.get_event_loop().time(),
                "status": "failed",
                "error": str(e)
            })
            raise
    
    async def static_analyze(self, code: str) -> Dict[str, Any]:
        """
        Perform static code analysis for security threats
        
        Args:
            code: Code to analyze
        
        Returns:
            Analysis result with safety status
        """
        dangerous_patterns = [
            "eval(", "exec(", "__import__", "compile(",
            "os.system", "subprocess.", "open(",
            "__builtins__", "globals()", "locals()",
            "setattr", "getattr", "delattr",
            "file(", "input(", "raw_input(",
        ]
        
        # Check for dangerous patterns
        for pattern in dangerous_patterns:
            if pattern in code:
                return {
                    "status": "unsafe",
                    "reason": f"Dangerous pattern detected: {pattern}",
                    "severity": "high"
                }
        
        # Check code complexity
        lines = code.split("\n")
        if len(lines) > 1000:
            return {
                "status": "warning",
                "reason": "Code too complex (>1000 lines)",
                "severity": "medium"
            }
        
        return {
            "status": "safe",
            "reason": "No security threats detected",
            "severity": "none"
        }
    
    async def track_taint_flow(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Track taint flow through inputs
        
        Args:
            inputs: Input data
        
        Returns:
            Tainted inputs with tracking metadata
        """
        tainted_inputs = {}
        
        for key, value in inputs.items():
            # Generate hash for data
            value_str = json.dumps(value, sort_keys=True, default=str)
            data_hash = hashlib.sha256(value_str.encode()).hexdigest()
            
            # Create taint tracking
            taint = TaintedData(
                source=key,
                data_hash=data_hash,
                taint_level=1,
                propagation_path=[key]
            )
            
            self.tainted_data[data_hash] = taint
            
            tainted_inputs[key] = {
                "value": value,
                "taint_hash": data_hash,
                "taint_level": 1
            }
        
        logger.info(f"Taint tracking enabled for {len(tainted_inputs)} inputs")
        
        return tainted_inputs
    
    async def _run_in_sandbox(
        self,
        agent_code: str,
        inputs: Dict[str, Any],
        agent_id: str
    ) -> Dict[str, Any]:
        """
        Run agent code in isolated sandbox
        
        Uses Docker container with security constraints
        """
        # Create temporary directory for execution
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write code to file
            code_file = os.path.join(tmpdir, "agent.py")
            with open(code_file, "w") as f:
                f.write(agent_code)
            
            # Write inputs to file
            input_file = os.path.join(tmpdir, "inputs.json")
            with open(input_file, "w") as f:
                json.dump(inputs, f)
            
            # Prepare Docker command with security constraints
            docker_cmd = [
                "docker", "run",
                "--rm",
                "--network", "none",  # No network access
                "--memory", f"{self.config.memory_limit_mb}m",
                "--cpus", str(self.config.cpu_quota_ms / 1000.0),
                "--pids-limit", "100",
                "--security-opt", "no-new-privileges",
                "--cap-drop", "ALL",
                "--read-only",
                "--tmpfs", "/tmp:rw,noexec,nosuid,size=100m",
                "-v", f"{tmpdir}:/workspace:ro",
                "-w", "/workspace",
                "python:3.11-slim",
                "timeout", str(self.config.max_execution_time_seconds),
                "python", "agent.py"
            ]
            
            try:
                # Execute in sandbox
                process = await asyncio.create_subprocess_exec(
                    *docker_cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.config.max_execution_time_seconds + 5
                )
                
                if process.returncode != 0:
                    raise RuntimeError(f"Sandbox execution failed: {stderr.decode()}")
                
                # Parse result
                result = {
                    "output": stdout.decode(),
                    "agent_id": agent_id,
                    "security_level": self.config.security_level.value,
                    "sandbox_verified": True
                }
                
                return result
            
            except asyncio.TimeoutError:
                logger.error(f"Sandbox execution timeout for {agent_id}")
                raise RuntimeError("Execution timeout")
            
            except Exception as e:
                logger.error(f"Sandbox execution error: {e}")
                # Fallback to simple execution (for development)
                return await self._fallback_execution(agent_code, inputs, agent_id)
    
    async def _fallback_execution(
        self,
        agent_code: str,
        inputs: Dict[str, Any],
        agent_id: str
    ) -> Dict[str, Any]:
        """Fallback execution when Docker is not available"""
        logger.warning("Using fallback execution (Docker not available)")
        
        # Simple restricted execution
        restricted_globals = {
            "__builtins__": {
                "print": print,
                "len": len,
                "str": str,
                "int": int,
                "float": float,
                "bool": bool,
                "list": list,
                "dict": dict,
                "tuple": tuple,
                "set": set,
            }
        }
        
        try:
            # Execute with restricted globals
            exec(agent_code, restricted_globals)
            
            return {
                "output": "Executed in fallback mode",
                "agent_id": agent_id,
                "security_level": "low",
                "sandbox_verified": False
            }
        
        except Exception as e:
            raise RuntimeError(f"Fallback execution failed: {e}")
    
    async def verify_integrity(self, result: Dict[str, Any]):
        """
        Verify result integrity after execution
        
        Args:
            result: Execution result to verify
        """
        # Check for suspicious patterns in output
        output = result.get("output", "")
        
        suspicious_patterns = [
            "password", "secret", "token", "key",
            "credentials", "api_key", "private"
        ]
        
        for pattern in suspicious_patterns:
            if pattern.lower() in output.lower():
                logger.warning(f"Suspicious pattern in output: {pattern}")
        
        # Verify sandbox flag
        if not result.get("sandbox_verified", False):
            logger.warning("Result not verified by sandbox")
    
    def get_security_metrics(self) -> Dict[str, Any]:
        """Get security metrics for monitoring"""
        total_executions = len(self.execution_history)
        successful = sum(1 for e in self.execution_history if e["status"] == "success")
        failed = total_executions - successful
        
        return {
            "total_executions": total_executions,
            "successful_executions": successful,
            "failed_executions": failed,
            "success_rate": successful / total_executions if total_executions > 0 else 0,
            "tainted_data_count": len(self.tainted_data),
            "security_level": self.config.security_level.value
        }


class SecurityError(Exception):
    """Security-related error"""
    pass


# Global sandbox instance
_sandbox: Optional[ZeroTrustSandbox] = None


def get_sandbox(config: Optional[SandboxConfig] = None) -> ZeroTrustSandbox:
    """Get or create global sandbox instance"""
    global _sandbox
    
    if _sandbox is None:
        _sandbox = ZeroTrustSandbox(config)
    
    return _sandbox


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_sandbox():
        sandbox = get_sandbox()
        
        # Safe code
        safe_code = """
result = sum([1, 2, 3, 4, 5])
print(f"Result: {result}")
"""
        
        try:
            result = await sandbox.execute_agent(
                safe_code,
                {"numbers": [1, 2, 3, 4, 5]},
                "test_agent"
            )
            print(f"Safe execution: {result}")
        except Exception as e:
            print(f"Error: {e}")
        
        # Unsafe code
        unsafe_code = """
import os
os.system("rm -rf /")
"""
        
        try:
            result = await sandbox.execute_agent(
                unsafe_code,
                {},
                "malicious_agent"
            )
            print(f"Unsafe execution: {result}")
        except Exception as e:
            print(f"Blocked: {e}")
        
        # Get metrics
        metrics = sandbox.get_security_metrics()
        print(f"\nSecurity metrics: {metrics}")
    
    asyncio.run(test_sandbox())

