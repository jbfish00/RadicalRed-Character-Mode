// Create a function at a known Thumb entry point (e.g. read out of a
// dispatch table, so the low bit was set — pass the address WITHOUT the
// Thumb bit) and print its decompilation. Unlike InspectRegions.java (which
// targets literal-pool addresses inside a function body), this takes real
// entry points, so it disassembles forward from the entry.
//
// Run via: analyzeHeadless <project> <name> -process <file> -noanalysis
//   -scriptPath <this dir> -postScript CreateAndDecompile.java <addr1> ...
// Addresses are hex WITH the 0x08000000 GBA ROM base included, e.g. 0907DD44
// (toAddr() resolves an un-prefixed offset to an unmapped address and silently no-ops).
// @category CharacterMode
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.lang.Register;
import ghidra.program.model.lang.RegisterValue;
import ghidra.program.model.listing.Function;
import ghidra.util.task.ConsoleTaskMonitor;
import java.math.BigInteger;

public class CreateAndDecompile extends GhidraScript {
    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length == 0) {
            println("USAGE: CreateAndDecompile.java <hexaddr1> <hexaddr2> ...  (Thumb entry points, no low bit)");
            return;
        }

        Register tmode = currentProgram.getProgramContext().getRegister("TMode");
        if (tmode == null) {
            println("ERROR: no TMode register found on this language - can't force Thumb mode");
            return;
        }

        DecompInterface ifc = new DecompInterface();
        ifc.openProgram(currentProgram);

        for (String hexaddr : args) {
            Address entry = toAddr(hexaddr);
            println("=== entry 0x" + hexaddr + " ===");

            Function func = getFunctionAt(entry);
            if (func == null) {
                // force Thumb from the entry forward before disassembling; use a
                // generous window since function length is unknown. A prior run
                // may already have disassembled (and context-locked) part of this
                // window — that's fine, the instructions that exist are already
                // Thumb; just skip the context write for the conflicting range.
                try {
                    currentProgram.getProgramContext().setRegisterValue(
                        entry, entry.add(0x1000), new RegisterValue(tmode, BigInteger.ONE));
                } catch (Exception e) {
                    println("  (context already set/conflicting across window - proceeding: " + e.getMessage() + ")");
                }
                disassemble(entry);
                func = createFunction(entry, null);
            }
            if (func == null) {
                func = getFunctionContaining(entry);
            }
            if (func == null) {
                println("  could not create/find a function here");
                continue;
            }
            println("  function: " + func.getName() + " @ " + func.getEntryPoint()
                    + "  size=" + func.getBody().getNumAddresses());
            DecompileResults res = ifc.decompileFunction(func, 90, new ConsoleTaskMonitor());
            if (res.decompileCompleted()) {
                println(res.getDecompiledFunction().getC());
            } else {
                println("  decompile failed: " + res.getErrorMessage());
            }
            println("");
        }
        ifc.dispose();
    }
}
