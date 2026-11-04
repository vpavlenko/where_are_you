const assert = require('node:assert/strict');
const fs = require('node:fs');
const {parseSchedule, convertedParts} = require('../dist/reader.js');
const page = fs.readFileSync('dist/index.html','utf8');
const config = JSON.parse(page.match(/<script id="reader-config" type="application\/json">([\s\S]*?)<\/script>/)[1]);
const parse = text => parseSchedule(text,config.mapping,config.paragraphCount);
const render = (text, step, schedule) => convertedParts(text,step,parse(schedule).stages,config.mapping).map(p=>p.text).join('');
assert.equal(render('Afrika a tlulatlula',1,'1 к т\n3 а'),'Afriкa a тluлaтluлa'.replaceAll('л','l'));
assert.equal(render('Afrika a tlulatlula',2,'1 к т\n3 а'),render('Afrika a tlulatlula',1,'1 к т\n3 а'));
assert.equal(render('Afrika a tlulatlula',3,'1 к т\n3 а'),'Аfriкa a тluлaтluлa'.replaceAll('л','l').replaceAll('a','а'));
assert.equal(render('Afrika',36,''),'Afrika');
assert.equal(render('K T k t',1,'1 к т'),'К Т к т');
assert.equal(render('x X y Y j J',1,'1 ш й дж'),'ш Ш й Й дж Дж');
assert.equal(render('w v',1,'1 в'),'в в');
assert.equal(parse('3 а\n1 а').stages.get('а'),1);
assert.equal(parse('1 к т\r\n\n3 а').errors.length,0);
for (const invalid of ['0 а','-1 а','37 а','1.5 а','1 q','1','<img src=x>','1 __proto__']) assert.equal(parse(invalid).errors.length,1,invalid);
assert.equal(parse(config.defaultSchedule).errors.length,0);
for (const part of convertedParts('Привет Afrika',36,parse(config.defaultSchedule).stages,config.mapping)) {
  if (/[А-Яа-яЁё]/u.test(part.text)) assert.equal(part.converted,true);
}
assert.equal((page.match(/class="paragraph-pair"/g)||[]).length,36);
assert.equal((page.match(/class="story-page/g)||[]).length,16);
console.log('Schedule boundaries, cumulative introduction, casing, highlighting, validation, and all 36 paragraph pairs: OK');
