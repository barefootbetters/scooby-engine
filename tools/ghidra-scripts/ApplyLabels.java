// Apply a WP-001 label list to the open Scooby.exe program.
//
// Each non-comment line of the list is "<hex address> <name>". The function
// at that address is created if auto-analysis missed it (several are reached
// only through vtables), then renamed. Names carry the engine's debug channel
// as a prefix: resource_, graphics_, audio_, script_, input_.
//
// Headless use (PowerShell), against a project that already holds an
// analyzed Scooby.exe:
//
//   & "$env:GHIDRA_HOME\support\analyzeHeadless.bat" C:\dev\scooby-engine\ghidra scooby `
//       -process Scooby.exe -noanalysis -scriptPath C:\dev\scooby-engine\tools\ghidra-scripts `
//       -postScript ApplyLabels.java C:\dev\scooby-engine\tools\ghidra-scripts\wp001-labels.txt
//
//@category Scooby
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.SourceType;
import java.nio.file.Files;
import java.nio.file.Paths;

public class ApplyLabels extends GhidraScript {
    @Override
    public void run() throws Exception {
        int labeled = 0;
        for (String line : Files.readAllLines(Paths.get(getScriptArgs()[0]))) {
            line = line.trim();
            if (line.isEmpty() || line.startsWith("#")) {
                continue;
            }
            String[] parts = line.split("\\s+");
            Address entry = toAddr(parts[0]);
            Function f = getFunctionAt(entry);
            if (f == null) {
                disassemble(entry);
                f = createFunction(entry, null);
            }
            if (f == null) {
                printerr("could not create a function at " + parts[0]);
                continue;
            }
            f.setName(parts[1], SourceType.USER_DEFINED);
            labeled++;
        }
        println("labeled " + labeled + " functions");
    }
}
