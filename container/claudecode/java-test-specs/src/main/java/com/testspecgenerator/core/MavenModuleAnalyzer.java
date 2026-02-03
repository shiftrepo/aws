package com.testspecgenerator.core;

import com.testspecgenerator.model.ModuleInfo;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.parser.Parser;
import org.jsoup.select.Elements;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * Analyzes Maven multi-module projects by parsing pom.xml files to extract
 * module information and validate module structure.
 */
public class MavenModuleAnalyzer {
    private static final Logger LOGGER = Logger.getLogger(MavenModuleAnalyzer.class.getName());

    /**
     * Analyzes a Maven multi-module project starting from the project root.
     *
     * @param projectRoot the root directory containing the parent pom.xml
     * @return list of ModuleInfo objects for all detected modules
     * @throws IOException if pom.xml cannot be read or parsed
     */
    public List<ModuleInfo> analyzeProject(Path projectRoot) throws IOException {
        LOGGER.info("Analyzing multi-module project at: " + projectRoot);

        Path parentPom = projectRoot.resolve("pom.xml");
        if (!Files.exists(parentPom)) {
            throw new IOException("Parent pom.xml not found at: " + parentPom);
        }

        List<String> moduleNames = extractModules(parentPom);
        if (moduleNames.isEmpty()) {
            LOGGER.warning("No modules found in parent pom.xml");
            return new ArrayList<>();
        }

        LOGGER.info("Found " + moduleNames.size() + " modules: " + moduleNames);

        List<ModuleInfo> modules = new ArrayList<>();
        for (String moduleName : moduleNames) {
            ModuleInfo moduleInfo = analyzeModule(projectRoot, moduleName);
            modules.add(moduleInfo);

            if (moduleInfo.isValid()) {
                LOGGER.info("[OK] Module validated: " + moduleName);
            } else {
                LOGGER.warning("[ERROR] Module validation failed: " + moduleName + " - " + moduleInfo.getValidationError());
            }
        }

        return modules;
    }

    /**
     * Extracts module names from a parent pom.xml file.
     *
     * @param pomFile path to the pom.xml file
     * @return list of module names found in the pom.xml
     * @throws IOException if the pom.xml cannot be read
     */
    public List<String> extractModules(Path pomFile) throws IOException {
        LOGGER.fine("Parsing pom.xml: " + pomFile);

        String content = Files.readString(pomFile, StandardCharsets.UTF_8);
        Document doc = Jsoup.parse(content, "", Parser.xmlParser());

        Elements modules = doc.select("project > modules > module");
        List<String> moduleNames = new ArrayList<>();

        for (Element moduleElement : modules) {
            String moduleName = moduleElement.text().trim();
            if (!moduleName.isEmpty()) {
                moduleNames.add(moduleName);
            }
        }

        LOGGER.fine("Extracted modules: " + moduleNames);
        return moduleNames;
    }

    /**
     * Analyzes a single module and creates a ModuleInfo object with validation.
     *
     * @param projectRoot the root directory of the multi-module project
     * @param moduleName the name/path of the module to analyze
     * @return ModuleInfo object with validation status
     */
    private ModuleInfo analyzeModule(Path projectRoot, String moduleName) {
        Path moduleRoot = projectRoot.resolve(moduleName);

        ModuleInfo.Builder builder = ModuleInfo.builder()
            .moduleName(getModuleDisplayName(moduleName))
            .moduleRoot(moduleRoot);

        // Check if module directory exists
        if (!Files.exists(moduleRoot) || !Files.isDirectory(moduleRoot)) {
            return builder
                .validationError("Module directory does not exist: " + moduleRoot)
                .build();
        }

        // Set up standard Maven directory structure
        Path sourceDir = moduleRoot.resolve("src/main/java");
        Path testDir = moduleRoot.resolve("src/test/java");
        Path coverageDir = moduleRoot.resolve("target/site/jacoco");
        Path pomPath = moduleRoot.resolve("pom.xml");

        builder.sourceDir(sourceDir)
               .testDir(testDir)
               .coverageDir(coverageDir)
               .pomPath(pomPath);

        // Validate module structure
        String validationError = validateModuleStructure(moduleRoot, testDir, pomPath);
        if (validationError != null) {
            builder.validationError(validationError);
        }

        return builder.build();
    }

    /**
     * Validates the structure of a module.
     *
     * @param moduleRoot the module root directory
     * @param testDir the test directory
     * @param pomPath the pom.xml path
     * @return validation error message, or null if valid
     */
    private String validateModuleStructure(Path moduleRoot, Path testDir, Path pomPath) {

        // Check for module pom.xml
        if (!Files.exists(pomPath)) {
            return "Module pom.xml not found: " + pomPath;
        }

        // Check for test directory (source directory is optional)
        if (!Files.exists(testDir)) {
            LOGGER.info("Test directory not found, module may not have tests: " + testDir);
            // Not a fatal error - module might not have tests yet
        } else if (!Files.isDirectory(testDir)) {
            return "Test path exists but is not a directory: " + testDir;
        }

        try {
            // Validate that pom.xml is readable
            String pomContent = Files.readString(pomPath, StandardCharsets.UTF_8);
            if (pomContent.trim().isEmpty()) {
                return "Module pom.xml is empty: " + pomPath;
            }
        } catch (IOException e) {
            return "Cannot read module pom.xml: " + e.getMessage();
        }

        return null; // Valid
    }

    /**
     * Extracts a display name from a module path.
     * For nested modules like "services/user-service", returns "user-service".
     *
     * @param moduleName the module path/name
     * @return display name for the module
     */
    private String getModuleDisplayName(String moduleName) {
        if (moduleName.contains("/")) {
            String[] parts = moduleName.split("/");
            return parts[parts.length - 1];
        }
        return moduleName;
    }

    /**
     * Checks if a directory appears to be a Maven multi-module project.
     *
     * @param projectRoot the directory to check
     * @return true if the directory contains a parent pom.xml with modules
     */
    public static boolean isMultiModuleProject(Path projectRoot) {
        try {
            Path pomFile = projectRoot.resolve("pom.xml");
            if (!Files.exists(pomFile)) {
                return false;
            }

            MavenModuleAnalyzer analyzer = new MavenModuleAnalyzer();
            List<String> modules = analyzer.extractModules(pomFile);
            return !modules.isEmpty();
        } catch (IOException e) {
            LOGGER.log(Level.WARNING, "Error checking if project is multi-module: " + e.getMessage(), e);
            return false;
        }
    }
}