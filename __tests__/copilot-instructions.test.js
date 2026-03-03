const fs = require('fs');
const path = require('path');
const markdownlint = require('markdownlint');

const COPILOT_INSTRUCTIONS_PATH = path.join(__dirname, '..', '.github', 'copilot-instructions.md');
const REQUIRED_SECTIONS = [
  'Copilot Coding Agent Instructions',
  'Repository Overview',
  'Development Workflow',
  'Build & Test',
  'Code Style',
  'Security & Secrets',
  'Validation'
];

describe('Copilot Instructions Validation', () => {
  let fileContent;
  let fileExists;

  beforeAll(() => {
    fileExists = fs.existsSync(COPILOT_INSTRUCTIONS_PATH);
    if (fileExists) {
      fileContent = fs.readFileSync(COPILOT_INSTRUCTIONS_PATH, 'utf8');
    }
  });

  describe('File Structure', () => {
    test('copilot-instructions.md should exist in .github directory', () => {
      expect(fileExists).toBe(true);
    });

    test('file should not be empty', () => {
      expect(fileContent).toBeDefined();
      expect(fileContent.length).toBeGreaterThan(0);
    });

    test('file should start with level-1 heading', () => {
      const lines = fileContent.split('\n');
      const firstNonEmptyLine = lines.find(line => line.trim().length > 0);
      expect(firstNonEmptyLine).toMatch(/^# /);
    });
  });

  describe('Required Sections', () => {
    test.each(REQUIRED_SECTIONS)('should contain "%s" section', (section) => {
      const headerPattern = new RegExp(`^#{1,2}\\s+${section.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`, 'm');
      expect(fileContent).toMatch(headerPattern);
    });

    test('sections should be in logical order', () => {
      const sectionIndices = REQUIRED_SECTIONS.map(section => {
        const match = fileContent.match(new RegExp(`^#{1,2}\\s+${section.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`, 'm'));
        return match ? fileContent.indexOf(match[0]) : -1;
      });

      // Check that all sections are found
      sectionIndices.forEach(index => {
        expect(index).toBeGreaterThan(-1);
      });

      // Check that they appear in order
      for (let i = 1; i < sectionIndices.length; i++) {
        expect(sectionIndices[i]).toBeGreaterThan(sectionIndices[i - 1]);
      }
    });

    test('each section should have content', () => {
      // Check each required section has content after it
      REQUIRED_SECTIONS.slice(1).forEach(section => {
        const sectionMatch = fileContent.match(
          new RegExp(`## ${section.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\n([\\s\\S]*?)(?=\\n## |$)`)
        );
        expect(sectionMatch).toBeTruthy();
        const sectionContent = sectionMatch[1].trim();
        expect(sectionContent.length).toBeGreaterThan(0);
      });
    });
  });

  describe('Content Quality', () => {
    test('Repository Overview should describe the repository state', () => {
      const overviewMatch = fileContent.match(/## Repository Overview\n([\s\S]*?)(?=\n## |$)/);
      expect(overviewMatch).toBeTruthy();
      const overviewContent = overviewMatch[1].toLowerCase();
      expect(overviewContent.length).toBeGreaterThan(50);
    });

    test('Development Workflow should mention branches or PRs', () => {
      const workflowMatch = fileContent.match(/## Development Workflow\n([\s\S]*?)(?=\n## |$)/);
      expect(workflowMatch).toBeTruthy();
      const workflowContent = workflowMatch[1].toLowerCase();
      expect(workflowContent).toMatch(/branch|pr|pull request|commit/);
    });

    test('Build & Test should mention testing approach', () => {
      const buildTestMatch = fileContent.match(/## Build & Test\n([\s\S]*?)(?=\n## |$)/);
      expect(buildTestMatch).toBeTruthy();
      const buildTestContent = buildTestMatch[1].toLowerCase();
      expect(buildTestContent).toMatch(/test|build|lint|run/);
    });

    test('Security & Secrets should warn against committing secrets', () => {
      const securityMatch = fileContent.match(/## Security & Secrets\n([\s\S]*?)(?=\n## |$)/);
      expect(securityMatch).toBeTruthy();
      const securityContent = securityMatch[1].toLowerCase();
      expect(securityContent).toMatch(/secret|token|credential|commit/);
    });
  });

  describe('Markdown Syntax', () => {
    test('should pass markdownlint validation', () => {
      const options = {
        files: [COPILOT_INSTRUCTIONS_PATH],
        config: {
          'default': true,
          'MD013': false, // Line length - often too strict for documentation
          'MD022': false, // Blanks around headings - style preference
          'MD032': false, // Blanks around lists - style preference
          'MD033': false, // Allow inline HTML if needed
          'MD041': false, // First line doesn't have to be top-level heading
        }
      };

      const result = markdownlint.sync(options);
      const resultString = result.toString();

      if (resultString) {
        console.log('Markdownlint issues:', resultString);
      }

      expect(resultString).toBe('');
    });

    test('should not have trailing whitespace on lines', () => {
      const lines = fileContent.split('\n');
      lines.forEach((line, index) => {
        expect(line).not.toMatch(/\s+$/);
      });
    });

    test('should use consistent list marker style', () => {
      const listLines = fileContent.split('\n').filter(line => line.match(/^\s*[-*+]\s/));
      if (listLines.length > 0) {
        const firstMarker = listLines[0].match(/^\s*([-*+])/)[1];
        listLines.forEach(line => {
          expect(line).toMatch(new RegExp(`^\\s*[${firstMarker}]\\s`));
        });
      }
    });
  });

  describe('Edge Cases and Validation', () => {
    test('should not contain placeholder text like TODO or TBD', () => {
      const upperContent = fileContent.toUpperCase();
      expect(upperContent).not.toMatch(/\bTODO\b/);
      expect(upperContent).not.toMatch(/\bTBD\b/);
      expect(upperContent).not.toMatch(/\bFIXME\b/);
    });

    test('should not have multiple consecutive blank lines', () => {
      expect(fileContent).not.toMatch(/\n\n\n+/);
    });

    test('should end with a single newline', () => {
      expect(fileContent).toMatch(/\n$/);
      expect(fileContent).not.toMatch(/\n\n$/);
    });

    test('headers should not have trailing punctuation', () => {
      const headers = fileContent.match(/^#{1,6}\s+.+$/gm) || [];
      headers.forEach(header => {
        expect(header).not.toMatch(/[.!?,;:]$/);
      });
    });

    test('should use proper ATX heading style (no closing hashes)', () => {
      const headers = fileContent.match(/^#{1,6}\s+.+$/gm) || [];
      headers.forEach(header => {
        expect(header).not.toMatch(/#+\s*$/);
      });
    });
  });

  describe('GitHub Integration', () => {
    test('file should be in .github directory for Copilot discovery', () => {
      expect(COPILOT_INSTRUCTIONS_PATH).toMatch(/\.github/);
    });

    test('file should have correct naming convention', () => {
      expect(path.basename(COPILOT_INSTRUCTIONS_PATH)).toBe('copilot-instructions.md');
    });
  });

  describe('Regression Tests', () => {
    test('should not revert to incomplete state', () => {
      // Ensure all core sections have substantial content (>30 chars each)
      REQUIRED_SECTIONS.slice(1).forEach(section => {
        const sectionMatch = fileContent.match(
          new RegExp(`## ${section.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\n([\\s\\S]*?)(?=\\n## |$)`)
        );
        expect(sectionMatch).toBeTruthy();
        const sectionContent = sectionMatch[1].trim();
        expect(sectionContent.length).toBeGreaterThan(30);
      });
    });

    test('should maintain consistent formatting style', () => {
      // Check that headers use ## for subsections
      const subsectionHeaders = fileContent.match(/^## [A-Z]/gm) || [];
      expect(subsectionHeaders.length).toBeGreaterThanOrEqual(6);
    });
  });

  describe('Negative Cases', () => {
    test('should not contain common typos in key terms', () => {
      const lowerContent = fileContent.toLowerCase();
      expect(lowerContent).not.toMatch(/repositry|respository/); // Common typo for repository
      expect(lowerContent).not.toMatch(/comit/); // Common typo for commit
      expect(lowerContent).not.toMatch(/workfow/); // Common typo for workflow
    });

    test('should not have broken markdown links', () => {
      const links = fileContent.match(/\[([^\]]+)\]\(([^)]+)\)/g) || [];
      links.forEach(link => {
        const urlMatch = link.match(/\[([^\]]+)\]\(([^)]+)\)/);
        const url = urlMatch[2];
        // URL should not be empty or just whitespace
        expect(url.trim().length).toBeGreaterThan(0);
        // Should not have obvious syntax errors
        expect(url).not.toMatch(/\s\s+/);
      });
    });

    test('should not contain excessive exclamation marks', () => {
      // Technical documentation should be professional
      const exclamationCount = (fileContent.match(/!/g) || []).length;
      const lineCount = fileContent.split('\n').length;
      expect(exclamationCount / lineCount).toBeLessThan(0.1);
    });
  });

  describe('Boundary Cases', () => {
    test('should handle files with exactly minimum required sections', () => {
      const sectionCount = (fileContent.match(/^## /gm) || []).length;
      expect(sectionCount).toBeGreaterThanOrEqual(REQUIRED_SECTIONS.length - 1);
    });

    test('should not exceed reasonable file size (10KB)', () => {
      expect(fileContent.length).toBeLessThan(10240);
    });

    test('should have reasonable line length averages', () => {
      const lines = fileContent.split('\n').filter(line => line.trim().length > 0);
      const totalLength = lines.reduce((sum, line) => sum + line.length, 0);
      const avgLength = totalLength / lines.length;
      expect(avgLength).toBeLessThan(200);
    });
  });
});