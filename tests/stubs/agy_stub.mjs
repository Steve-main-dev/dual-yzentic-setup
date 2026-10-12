// Stand-in for the `agy` CLI. Records its arguments, then behaves as $STUB_MODE says.
// Pure Node standard library; run as `node agy_stub.mjs <the arguments agy would get>`.
import { appendFileSync, mkdirSync, writeFileSync } from 'node:fs';
import { dirname } from 'node:path';

if (process.env.STUB_ARGS_FILE) {
  appendFileSync(process.env.STUB_ARGS_FILE, JSON.stringify(process.argv.slice(2)) + '\n');
}

function write(path, text, append = false) {
  mkdirSync(dirname(path), { recursive: true });
  (append ? appendFileSync : writeFileSync)(path, text);
}

function report(extra = {}) {
  console.log(JSON.stringify({
    conversation_id: 'stub-conversation',
    status: 'SUCCESS',
    response: 'ok',
    duration_seconds: 1.5,
    num_turns: 1,
    usage: { input_tokens: 1000, output_tokens: 234, total_tokens: 1234 },
    ...extra
  }));
}

const mode = process.env.STUB_MODE || 'success';

if (mode === 'success') {
  console.log('warning: stub warning line before the JSON');
  report();
} else if (mode === 'write_test') {
  write('tests/generated.test.js', 'test("generated", () => {});\n');
  report();
} else if (mode === 'write_source') {
  write('src/rogue.js', 'module.exports = "rogue";\n');
  report();
} else if (mode === 'modify_source') {
  write('src/app.js', '// touched by the stub\n', true);
  report();
} else if (mode === 'denied') {
  report({ response: '', denied_actions: [{ action: 'command', display_name: 'RunCommand' }] });
} else if (mode === 'garbage') {
  console.log('this is not json\n\nsecond line\nthird line\nfourth line');
} else if (mode === 'sleep') {
  setTimeout(() => report(), Number(process.env.STUB_SLEEP || 60) * 1000);
} else if (mode === 'status_timeout') {
  report({ status: 'TIMEOUT', response: '', usage: { total_tokens: 77 } });
} else if (mode === 'fail_exit') {
  console.error('error: invalid model selection');
  process.exit(3);
}
