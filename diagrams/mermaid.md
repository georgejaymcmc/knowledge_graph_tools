   subgraph 1 Static repo context 
   A("`**Inspect current repo**`")
   B("`**Git context**
    *- Branch, status, commits*`")
   C("`**Project docs**
    *- AGENTS.md
    - README.md, etc.*`")
   A-->|"#9312;"|B
   A-->|"#9313;"|C
   D("`**Workspace**
   *- Summary*`")
   B-->|"#9314;"|D
   C-->|"#9315;"|D
   E("`**Stable prompt prefix**
   *- Rules, tools, workspace summary* `")
   D-->|"#9316;"|E
   end
   F("`**User request**
   - &quot;Write unit tests for function xyz&quot;`")
   G("`**Prompt assembly**
   *- Prefix + memory + transcript + request*`")
   F-->|"#9317;"|G
   E-->|"#9318;"|G
   H("`**LLM**`")
   I("`**Model response**
   *- Tool call or final answer*`")
   G-->|"#9319;"|H
   H-->|"#9320;"|I
   subgraph 2 Runtime updates 
   J("`**Compact transcript**
   *- Recent history*`")
      K("`**Working memory**
   *- Task, files, notes*`")
   end
   J-->|"#9321;"|G
   K-->|"#9322;"|G
   subgraph 3 Tool access and Use
   L("`**Validate**
   *- Check tool and args`")
   M("`**Approve**
   *- Yes/No*`")
   L-->|"#9323;"|M
   N("`**Run tool**
   - *Execute tool call*`")
   M-->|"#9324;"|N
   O("`**Clip**
   - *Get truncated tool response*`")
   N-->|"#9325;"|O
   end
   O-->|"#9326;"|J
   I-->|"#9327;"|L
   subgraph 4 Minimising context bloat
   P("`**Search results**`")
   Q("`**Shell logs**`")
   R("`**Repeated reads**`")
   S("`**Clip**
   *- Reduce raw output size*`")
   P-->|"#9328;"|S
   Q-->|"#9329;"|S
   T("`**Deduplicate**
   *- Older read_file events*`")
   R-->|"#9330;"|T
   U("`**Full Transcript**
   *- User requests, tool results, LLM reponses*`")
   U-->|"#9331;"|T
   V("`**Asymmetric detail**
   *- Recent rich, older short*`")
   V-->|"#12881;"|T
   end
   S-->|"#12882;"|J
   T-->|"#12883;"|J
   subgraph 5 Stored session state
   W("`**New events**
   *- User turns, tool results, LLM responses*`")
   X("`**Full transcript**
   *- User requests, tool results, LLM responses*`")
   end
   W-->|"#12884;"|X
   W-->|"#12885;"|K
   X-->|"#12886;"|J
   Y("`**Delegate subtask**
   *- Spawn subagent*`")
   I-->|"#12887;"|Y
   subgraph 6 Subagent prompt
   AA("`**Child prompt**
   *- Task + inherited text*`")
   AB("`**Boundaries**
   *- Read-only, limited steps*`")
   AC("`**Subagent findings**
   *- Return results to main loop*`")
   end
   Y-->|"#12888;"|AA
   AA-->|"#12889;"|H
   AB-->|"#12890;"|H
   H-->|"#12890;"|AC
   AC-->|"#12891;"|G