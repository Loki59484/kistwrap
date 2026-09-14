import java.util.*;
import java.util.concurrent.Callable;
import java.net.URL;
import javax.naming.*;
import javax.swing.JFrame;
import javax.swing.JMenu;
import javax.swing.JMenuItem;
import javax.swing.JOptionPane;
import javax.xml.parsers.FactoryConfigurationError;
import java.awt.event.*;
import java.io.*;
import kisthep.util.*;
import java.util.logging.Logger;
import picocli.CommandLine;
import picocli.CommandLine.Command;
import picocli.CommandLine.Mixin;
import picocli.CommandLine.Option;
import kisthep.file.*;

public class CLIinterface {

    
    public static final class Console {

        public static final Scanner SCANNER = new Scanner(System.in);

        private Console() {
        }
    }

    public static void setTemp(Session workSession, List<Double> temp)
            throws TemperatureStepException, TemperatureException, runTimeException, IllegalDataException {

        if (temp.size() == 1) {
            workSession.setTemperatureMin(temp.get(0));
            workSession.setTemperatureMax(temp.get(0));
        } else if (temp.size() == 2) {
            workSession.setTemperatureMin(temp.get(0));
            workSession.setTemperatureMax(temp.get(1));
            workSession.setStepTemperature(1.0);
        } else if (temp.size() == 3) {
            workSession.setTemperatureMin(temp.get(0));
            workSession.setTemperatureMax(temp.get(1));
            workSession.setStepTemperature(temp.get(2));
        } else {
            System.err.println("Invalid Value for temperature");
            throw new IllegalDataException();
        }
    }

    public static void setPressure(Session workSession, List<Double> pressure)
            throws PressureException, PressureStepException, runTimeException, IllegalDataException {

        if (pressure.size() == 1) {
            workSession.setPressureMin(pressure.get(0));
            workSession.setPressureMax(pressure.get(0));
        } else if (pressure.size() == 2) {
            workSession.setPressureMin(pressure.get(0));
            workSession.setPressureMax(pressure.get(1));
            workSession.setStepPressure(1.0);
        } else if (pressure.size() == 3) {
            workSession.setPressureMin(pressure.get(0));
            workSession.setPressureMax(pressure.get(1));
            workSession.setStepPressure(pressure.get(2));
        } else {
            System.err.println("Invalid Value for temperature");
            throw new IllegalDataException();
        }

    }

    public static void guiLancher() {
        String path = null;

        // LET'S GO
        path = System.getProperty("user.dir");
        Kistep.setUserCurrentDirectory(path);
        Interface fenetre = new Interface();

        fenetre.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        fenetre.setVisible(true);
        Kistep.currentInterface = fenetre;
    }

    public static class FileOptions {

        // CLI options to accept input/session filepath and output filepaths
        @Option(names = {"-i",
            "--inputfile"}, description = "Enter a session file (.kstp) or Input file(.kinp)")
        private File inputfile;

        public File getInputfile() {
            return this.inputfile;
        }

        @Option(names = {"-o", "-outputfile"}, description = "Enter path for an output file")
        private File outputfile;

        public File getOutputfile() {
            return this.outputfile;
        }
    }


    public static class CalcOptions {
        // Parameters to set calculation parameters
        @Option(names = "-y", description = "Assumes yes for all yes/no questions.")
        private boolean yesToAll;

        public boolean getyesToAll() {
            return this.yesToAll;
        }

        @Option(names = {"-T",
            "--Temperature"}, split = ",", description = "Sets Temperature values for a calculation in Kelvin. Expects input in the form: tMin, tMax, steps")
        private List<Double> temperature;

        public List<Double> getTemp() {
            return this.temperature;
        }

        @Option(names = {"-P",
            "--Pressure"}, split = ",", description = "Sets Pressure values for a calculation. Expects input in the form: pMin, pMax, steps")
        private List<Double> pressure;

        public List<Double> getPressure() {
            return this.pressure;
        }

        @Option(names = {"-sr", "--show-results"}, description = "Displays results in KISTEP panel.")
        private boolean showResult;

        public boolean getShowresult() {
            return this.showResult;
        }

        @Option(names = {"-sd", "--save-data"}, description = "Saves data used to plot graphics of a calculations.")
        private boolean saveFlag;

        enum calcType {
            UNI, BI
        }

        @Option(names = "--moltype", description = "Enter the molecularity of the reaction : UNI or BI", defaultValue = "BI")
        private calcType calctype;

        public calcType getcalcType() {
            return this.calctype;
        }

    }

    public static class BimolOptions {

        @Option(names = "-r1", description = "Path of file for Reactant 1.", required = true)
        private File react1File;

        public File getreact1File() {
            return this.react1File;
        }

        @Option(names = "-r2", description = "Path of file for Reactant 2.", required = true)
        private File react2File;

        public File getreact2File() {
            return this.react2File;
        }

        @Option(names = "-rpath", description = "Path of file for reaction path.", required = true)
        private File rpathFile;

        public File getrpathFile() {
            return this.rpathFile;
        }

    }

    // SETUP SESSION
    @Command(name = "session", description = "Sets up a session. \"NEW\" creates a new session. \"OPEN\" opens a session from the session file")
    public static class StartSession implements Callable<Integer> {

        private Session workSession;

        public Session getsSession() {
            return this.workSession;
        }

        @Mixin
        private FileOptions sessionFiles;

        enum Sessiontype {
            NEW, OPEN
        }

        @Option(names = {"-t", "--type"}, description = "Session type: NEW or OPEN", defaultValue = "NEW")
        private Sessiontype sessiontype;

        public Sessiontype getSessiontype() {
            return this.sessiontype;
        }

        @Override
        public Integer call() {
            if (this.getSessiontype() == Sessiontype.OPEN) {
                if (sessionFiles.getInputfile() == null) {
                    System.err.println("Error: A file path must be specified with --session=OPEN");
                    return 1; // Error
                } else {
                    System.out.println("Opening session from file :" + sessionFiles.getInputfile().getAbsolutePath());
                    guiLancher();
                    Kistep.currentInterface.triggerOpenAction(sessionFiles.getInputfile());
                }
            } else {
                System.out.println("Creating a new session");
                workSession = new Session();
            }
            return 0;
        }
    }

    // SETUP CALCULATION
    @Command(name = "calc", description = "Initiates the given type of calculation.", subcommands = {
        Calculations.CalcRpath.class, Calculations.CalcMolec.class, Calculations.CalcVTST.class,
        Calculations.CalcTST.class })
    public static class Calculations implements Callable<Integer> {

        @Override
        public Integer call() {
            System.err.println("Error: Please specify a calculation type (e.g., 'rpath').");
            new CommandLine(this).usage(System.err);
            return 1;
        }

        // REACTION PATH CALCULATION
        @Command(name = "Rpath", description = "Creates a reaction path for given files. Requires number of points to be read.", mixinStandardHelpOptions = true)
        public static class CalcRpath implements Callable<Integer> {

            Session workSession = new Session();

            @Mixin
            private FileOptions sessionFiles;

            @Mixin
            CalcOptions calcoptions;

            @Option(names = "--pts", required = true, description = "Please enter the number of points to be read (TST=1, VTST=n) including the TS itself ")
            private int nbPts;

            @Option(names = "--ircpoints", required = true, description = "Please enter an array of path points seperated by comma. Eg : -1.0,-0.9...,0.0,...0.9,1.0", split = ",")
            private ArrayList<Double> irc;

            @Option(names = "--kinpfiles", required = true, description = "Please enter path for .kinp files corresponding to the order of irc points provided.", split = ",")
            private ArrayList<File> rawinputFiles;

            File temporaryFile;
            File temporaryFile2;
            ActionOnFileRead readFromCurrentKinp;
            ActionOnFileWrite writeOnRPKinp;
            String temporaryFileName = "";
            String temporaryFileName2 = "";
            String currentLine;
            Boolean notAGoodName;
            Boolean alreadyOpen;
            ArrayList<File> kinpFiles = new ArrayList<>();

            public Integer call() {
                try {
                    ChemicalSystem.cli = true; // Setting commad line flag

                    System.out.println("Starting RPath Calculations for " + nbPts + " points and "
                            + rawinputFiles.size() + " Files");
                    if (nbPts <= 0) {
                        throw new CancelException();
                    } else if (nbPts == 1) {
                        irc.clear();
                        irc.add(0.0);// TST case
                    }

                    for (File file : rawinputFiles) {
                        temporaryFile = ChemicalSystem.returnKinpFile(ChemicalSystem.pathPoint, file);
                        kinpFiles.add(temporaryFile);
                    }
                    temporaryFileName = sessionFiles.getOutputfile().getAbsolutePath();

                    if (!temporaryFileName.endsWith(".kinp")) {
                        System.out.println(".kinp will be appended to the output file.");
                        temporaryFileName = temporaryFileName + ".kinp";
                    }

                    notAGoodName = true;
                    while (notAGoodName) {
                        // check that this file is not already open (one of the kinp files in memory)
                        alreadyOpen = false;
                        for (int iFile = 0; iFile < nbPts; iFile++) {
                            // get the absolute filename of the kinp file of the current path point
                            temporaryFile2 = (kinpFiles.get(iFile));
                            temporaryFileName2 = temporaryFile2.getAbsolutePath();

                            // compare to the wanted filename for the reaction path:
                            if (temporaryFileName2.equals(temporaryFileName)) {
                                alreadyOpen = true;
                                System.err.println(
                                        "Sorry, this file is already in use in KiSThelP session. Please choose another name.");
                                break;
                            }
                        }

                        if (alreadyOpen == false) {

                            File f = new File(temporaryFileName);
                            if (f.exists()) {
                                if (!calcoptions.getyesToAll()) {
                                    System.out.println(
                                            "This file Already exists and will be overwritten if you continue. Do you want to proceed? (Y/N) : ");
                                    String input = Console.SCANNER.nextLine();
                                    if (input.equals("y") || input.equals("Y") || input.equals("yes")
                                            || input.equals("YES")) {
                                        notAGoodName = false;
                                    } else {
                                        System.out.println("Exiting with error.");
                                        return 1;
                                    }
                                } else {
                                    notAGoodName = false;
                                }
                            } else {
                                notAGoodName = false;
                            }
                        }
                    }
                    writeOnRPKinp = null;
                    writeOnRPKinp = new ActionOnFileWrite(temporaryFileName);
                    for (int iFile = 0; iFile < nbPts; iFile++) {
                        // write the IRC Header
                        writeOnRPKinp.oneString(Keywords.startOfPointInputSection);
                        writeOnRPKinp.oneString(Keywords.startOfReactionCoordinateInputSection);
                        writeOnRPKinp.oneDouble(irc.get(iFile));
                        writeOnRPKinp.oneString(Keywords.endOfInputSection);

                        // now: directly copy the information from the kinp file to the reactionPath
                        // file
                        // write the kinp file content of the current point
                        temporaryFile = (kinpFiles.get(iFile));
                        temporaryFileName = temporaryFile.getAbsolutePath();

                        readFromCurrentKinp = new ActionOnFileRead(temporaryFileName, Constants.kInpFileType);
                        currentLine = readFromCurrentKinp.oneString();

                        // reading loop
                        if (currentLine == null) {
                            System.err.println("Warning : the file " + temporaryFileName + " is empty ...");
                        } else {
                            do {
                                writeOnRPKinp.oneString(currentLine);
                                currentLine = readFromCurrentKinp.oneString();
                            } while (currentLine != null);
                        } // end of else
                        // write the IRC tail keyword
                        writeOnRPKinp.oneString(Keywords.endOfPointSection);

                        // remove the temporary current Kinp file from the Kisthelp list AND next erase
                        // the file
                        readFromCurrentKinp.end();
                        readFromCurrentKinp.getWorkFile().delete();

                    } 
                    writeOnRPKinp.end();
                    System.out
                            .println("Output file " + writeOnRPKinp.getWorkFile().getName() + " successfully written.");
                    return 0;
                } catch (CancelException error) {
                    new CommandLine(this).usage(System.err);
                    return 1;
                } catch (IOException error) {
                    new CommandLine(this).usage(System.err);
                    return 1;
                } catch (IllegalDataException error) {
                    new CommandLine(this).usage(System.err);
                    return 1;
                }

            }
        }// End of CalcRpath

        // THERMODYNAMIC CALCULATION FOR ATOMS/MOLECULES
        @Command(name = "Molec", description = "Saves a kinp file for the given atom/molecule containing its thermodynamic properties.", mixinStandardHelpOptions = true)
        public static class CalcMolec implements Callable<Integer> {

            Session workSession = new Session();

            @Mixin
            private FileOptions sessionFiles;

            @Mixin
            CalcOptions calcoptions;

            public Integer call() {
                try {
                    ChemicalSystem.cli = true;
                    workSession.getFilesToBeRead().add("the system");
                    workSession.add(
                            new InertStatisticalSystem(workSession.getTemperatureMin(), workSession.getPressureMin(),
                                    sessionFiles.getInputfile()));

                    // make available the results save menu if session is not empty AND !! if the
                    // single temperature or pressure range is invoked
                    if ((Session.getCurrentSession().getTemperatureMin() == Session.getCurrentSession()
                            .getTemperatureMax())
                            && (Session.getCurrentSession().getPressureMin() == Session.getCurrentSession()
                            .getPressureMax())) {
                        // saveResults.setEnabled(true);
                    } else {
                        // saveResults.setEnabled(false);
                    }

                    // resetSetEnabled(true);
                    // saveInputs.setEnabled(true);
                    // reactPathBuild.setEnabled(false);
                    // display results
                    if (calcoptions.getShowresult()) {
                        guiLancher();
                        workSession.displayResults();
                    }
                    System.out.println(".kinp files written successfully.");
                    return 0;

                } catch (CancelException error) {
                    new CommandLine(this).usage(System.err);
                    return 1;
                } catch (IllegalDataException error) {
                    new CommandLine(this).usage(System.err);
                    return 1;
                } catch (IOException error) {
                    new CommandLine(this).usage(System.err);
                    return 1;
                } catch (runTimeException error) {
                    new CommandLine(this).usage(System.err);
                    return 1;
                } catch (OutOfRangeException error) {
                    new CommandLine(this).usage(System.err);
                    return 1;
                }

            }

        }

        // TST
        @Command(name = "TST", description = "Performs a TST calculations.", mixinStandardHelpOptions = true)
        public static class CalcTST implements Callable<Integer> {

            Session workSession = new Session();

            @Mixin
            private FileOptions sessionFiles;

            @Mixin
            private BimolOptions bimoloptions;

            @Mixin
            private CalcOptions calcoptions;

            enum tunnelType {
                Wig, Eck
            }

            @Option(names = "--tunnelling", description = "Adds provided type of tunnelling correction to the calculation. Possible values: Wig, Eck")
            private tunnelType tunneltype;

            @Option(names = {"-revb",
                "--reverse-barrier"}, description = "Adds provided type of tunnelling correction to the calculation. Possible values: Wig, Eck")
            private double revBarrier;

            private void Bimol() throws CancelException, IllegalDataException, PressureException, IOException,
                    runTimeException, OutOfRangeException {

                try {

                    if (tunneltype == tunnelType.Wig) {
                        workSession.add(new BiMolecularReaction(workSession.getTemperatureMin(), "tst_w",
                                bimoloptions.getreact1File(), bimoloptions.getreact2File(),
                                bimoloptions.getrpathFile()));

                    } else if (tunneltype == tunnelType.Eck) {
                        workSession.add(new BiMolecularReaction(workSession.getTemperatureMin(), "tst_eck",
                                bimoloptions.getreact1File(), bimoloptions.getreact2File(),
                                bimoloptions.getrpathFile(), revBarrier));
                    } else if (tunneltype == null) {
                        workSession.add(new BiMolecularReaction(workSession.getTemperatureMin(), "tst",
                                bimoloptions.getreact1File(), bimoloptions.getreact2File(),
                                bimoloptions.getrpathFile()));
                    } else {
                        throw new IllegalDataException();
                    }

                    // note that here, we don't give any pressure
                    // parameter; P will be = P0 (in Reaction Class)
                    // since pressure is necessary P0 at the beginning of this calculation, we have
                    // to
                    // update the pressure of the current session content to P0 (and also the txt
                    // display in the pressure field)
                    // indeed, the user may have changed the pressure in the previous calculation
                    // before reset
                    // testing the mode (pressure value or pressure range)
                    if (workSession.getPressureMin() == workSession.getPressureMax()) // we are in mode single
                    // pressure
                    {
                        try {
                            // remind that the pressure parameter in method setPressure must always be given
                            // as a number in the user UNIt !!
                            // the method setpressure will convert it in the Kisthelp UNIt for pressure (Pa)
                            workSession.setPressureMin(
                                    Session.getCurrentSession().getUnitSystem()
                                            .convertToPressureUnit(Constants.P0));
                            workSession.setPressureMax(
                                    Session.getCurrentSession().getUnitSystem()
                                            .convertToPressureUnit(Constants.P0));
                        } catch (PressureException error) {
                            System.err.println("Warning : The Pressure must be positive");
                        } catch (runTimeException error) {
                            new CommandLine(this).usage(System.err);
                        } catch (IllegalDataException error) {
                            new CommandLine(this).usage(System.err);
                        }
                        // display results
                        if (sessionFiles.getOutputfile() != null) {
                            String filename = sessionFiles.getOutputfile().getAbsolutePath();
                            // correction: 11/01/2009
                            // check the filename suffix
                            if (!filename.endsWith(".kstp")) {
                                System.out.println(".kstp will be appended to the output file");
                                workSession.save(filename + ".kstp");
                            } else {
                                workSession.save(filename);
                            } // end of if
                            System.out.println("Session saved successfully.");
                        }
                        if (calcoptions.getShowresult()) {
                            guiLancher();
                            workSession.displayResults();
                        }
                    }
                } catch (CancelException error) {
                    new CommandLine(this).usage(System.err);
                    throw new CancelException();
                } catch (IllegalDataException error) {
                    new CommandLine(this).usage(System.err);
                    throw new IllegalDataException();
                } catch (IOException error) {
                    new CommandLine(this).usage(System.err);
                    throw new IOException();
                } catch (runTimeException error) {
                    new CommandLine(this).usage(System.err);
                    throw new runTimeException();
                } catch (OutOfRangeException error) {
                    new CommandLine(this).usage(System.err);
                    throw new OutOfRangeException();
                }
            }

            public Integer call() {
                try {
                    if (calcoptions.saveFlag && !calcoptions.showResult) {
                        System.err.println("-ss/--save-data command can only be used with -sr/--show-results");
                        return 1;
                    }
                    if (calcoptions.saveFlag) {
                        BiMolecularReaction.cli = true;
                        BiMolecularReaction.workfile = bimoloptions.rpathFile;
                    }
                    ChemicalSystem.cli = true;
                    if (calcoptions.getPressure() != null) {
                        System.out.println("Pressure settings :" + calcoptions.getPressure());
                        setPressure(this.workSession, calcoptions.getPressure());
                    }

                    if (calcoptions.getTemp() != null) {
                        setTemp(this.workSession, calcoptions.getTemp());
                    }

                    if (calcoptions.getcalcType().equals(CalcOptions.calcType.BI)) {

                        Bimol();
                    }
                } catch (TemperatureStepException error) {
                    new CommandLine(this).usage(System.err);
                    return 1;
                } catch (TemperatureException error) {
                    new CommandLine(this).usage(System.err);
                    return 1;
                } catch (PressureStepException error) {
                    new CommandLine(this).usage(System.err);
                    return 1;
                } catch (PressureException error) {
                    new CommandLine(this).usage(System.err);
                    return 1;
                } catch (CancelException error) {
                    new CommandLine(this).usage(System.err);
                    return 1;
                } catch (IllegalDataException error) {
                    new CommandLine(this).usage(System.err);
                    return 1;
                } catch (IOException error) {
                    new CommandLine(this).usage(System.err);
                    return 1;
                } catch (runTimeException error) {
                    new CommandLine(this).usage(System.err);
                    return 1;
                } catch (OutOfRangeException error) {
                    new CommandLine(this).usage(System.err);
                    return 1;
                }

                return 0;
            }

        }

        // VTST
        @Command(name = "VTST", description = "Performs a VTST calculations.", mixinStandardHelpOptions = true)
        public static class CalcVTST implements Callable<Integer> {

            Session workSession;

            @Mixin
            private FileOptions sessionFiles;

            @Mixin
            private BimolOptions bimoloptions;

            @Mixin
            private CalcOptions calcoptions;

            enum tunnelType {
                Wig, Eck
            }

            @Option(names = "--tunnelling", description = "Adds provided type of tunnelling correction to the calculation. Possible values: Wig, Eck")
            private tunnelType tunneltype;

            @Option(names = {"-revb",
                "--reverse-barrier"}, description = "Reverse energy barrier for the reaction path. Requrired for Eckart correction. Must be in kJ/mol.", defaultValue = "0.0")
            private double revBarrier;

            private void Bimol() throws CancelException, IllegalDataException, PressureException, IOException,
                    runTimeException, OutOfRangeException {

                try {

                    if (tunneltype == tunnelType.Wig) {
                        workSession.add(new BiMolecularReaction(workSession.getTemperatureMin(), "vtst_w",
                                bimoloptions.getreact1File(), bimoloptions.getreact2File(),
                                bimoloptions.getrpathFile()));

                    } else if (tunneltype == tunnelType.Eck) {
                        workSession.add(new BiMolecularReaction(workSession.getTemperatureMin(), "vtst_eck",
                                bimoloptions.getreact1File(), bimoloptions.getreact2File(),
                                bimoloptions.getrpathFile(), revBarrier));
                    } else if (tunneltype == null) {
                        workSession.add(new BiMolecularReaction(workSession.getTemperatureMin(), "vtst",
                                bimoloptions.getreact1File(), bimoloptions.getreact2File(),
                                bimoloptions.getrpathFile()));
                    } else {
                        throw new IllegalDataException();
                    }

                    // note that here, we don't give any pressure
                    // parameter; P will be = P0 (in Reaction Class)
                    // since pressure is necessary P0 at the beginning of this calculation, we have
                    // to
                    // update the pressure of the current session content to P0 (and also the txt
                    // display in the pressure field)
                    // indeed, the user may have changed the pressure in the previous calculation
                    // before reset
                    // testing the mode (pressure value or pressure range)
                    if (workSession.getPressureMin() == workSession.getPressureMax()) // we are in mode single
                    // pressure
                    {
                        try {
                            // remind that the pressure parameter in method setPressure must always be given
                            // as a number in the user UNIt !!
                            // the method setpressure will convert it in the Kisthelp UNIt for pressure (Pa)
                            workSession.setPressureMin(
                                    Session.getCurrentSession().getUnitSystem()
                                            .convertToPressureUnit(Constants.P0));
                            workSession.setPressureMax(
                                    Session.getCurrentSession().getUnitSystem()
                                            .convertToPressureUnit(Constants.P0));

                        } catch (PressureException error) {
                            System.err.println("Warning : The Pressure must be positive");
                        } catch (runTimeException error) {
                            new CommandLine(this).usage(System.err);
                        } catch (IllegalDataException error) {
                            new CommandLine(this).usage(System.err);
                        }
                        // display results
                        if (sessionFiles.getOutputfile() != null) {
                            String filename = sessionFiles.getOutputfile().getAbsolutePath();
                            // correction: 11/01/2009
                            // check the filename suffix
                            if (!filename.endsWith(".kstp")) {
                                System.out.println(".kstp will be appended to the output file");
                                workSession.save(filename + ".kstp");
                            } else {
                                workSession.save(filename);
                            } // end of if
                            System.out.println("Session saved successfully.");
                        }
                        if (calcoptions.getShowresult()) {
                            workSession.displayResults();
                        }
                    }
                } catch (CancelException error) {
                    new CommandLine(this).usage(System.err);
                    throw new CancelException();
                } catch (IllegalDataException error) {
                    new CommandLine(this).usage(System.err);
                    throw new IllegalDataException();
                } catch (IOException error) {
                    new CommandLine(this).usage(System.err);
                    throw new IOException();
                } catch (runTimeException error) {
                    new CommandLine(this).usage(System.err);
                    throw new runTimeException();
                } catch (OutOfRangeException error) {
                    new CommandLine(this).usage(System.err);
                    throw new OutOfRangeException();
                }
            }

            public Integer call() {
                try {
                    if (calcoptions.getShowresult()) {
                        guiLancher();
                        workSession = Session.getCurrentSession();
                    }

                    if (tunneltype != tunnelType.Eck && revBarrier != 0.0) {
                        System.err.println(
                                "--reverse-barrier provided but not applicable for the selected type of calculation, hence it will be ignored");
                    }

                    if (tunneltype == tunnelType.Eck && revBarrier == 0.0) {

                        System.err.println(
                                "--reverse-barrier is required for calculatioins involving Eckart tunnelling correction (--tunnelling=Eck) ");
                        return 1;
                    }

                    if (calcoptions.saveFlag && !calcoptions.showResult) {
                        System.err.println("-sd/--save-data command can only be used with -sr/--show-results");
                        return 1;
                    }
                    if (calcoptions.saveFlag) {
                        BiMolecularReaction.cli = true;
                        BiMolecularReaction.workfile = bimoloptions.rpathFile;
                    }
                    ChemicalSystem.cli = true;
                    if (calcoptions.getPressure() != null) {
                        System.out.println("Pressure settings :" + calcoptions.getPressure());
                        setPressure(this.workSession, calcoptions.getPressure());
                    }

                    if (calcoptions.getTemp() != null) {
                        setTemp(this.workSession, calcoptions.getTemp());
                    }

                    if (calcoptions.getcalcType().equals(CalcOptions.calcType.BI)) {

                        Bimol();

                    }

                } catch (TemperatureStepException error) {
                    new CommandLine(this).usage(System.err);
                    return 1;
                } catch (TemperatureException error) {
                    new CommandLine(this).usage(System.err);
                    return 1;
                } catch (PressureStepException error) {
                    new CommandLine(this).usage(System.err);
                    return 1;
                } catch (PressureException error) {
                    new CommandLine(this).usage(System.err);
                    return 1;
                } catch (CancelException error) {
                    new CommandLine(this).usage(System.err);
                    return 1;
                } catch (IllegalDataException error) {
                    new CommandLine(this).usage(System.err);
                    return 1;
                } catch (IOException error) {
                    new CommandLine(this).usage(System.err);
                    return 1;
                } catch (runTimeException error) {
                    new CommandLine(this).usage(System.err);
                    return 1;
                } catch (OutOfRangeException error) {
                    new CommandLine(this).usage(System.err);
                    return 1;
                }

                return 0;
            }

        }

        // EQUILIBRIUM
        @Command(name = "EQUIL", description = "Performs an equilibrium calculations.", mixinStandardHelpOptions = true)
        public static class CalcEquil {
            
            Session workSession;

            @Mixin
            private FileOptions sessionFiles;

            @Mixin
            private BimolOptions bimoloptions;

            @Mixin
            private CalcOptions calcoptions;            
        }
    }

}
