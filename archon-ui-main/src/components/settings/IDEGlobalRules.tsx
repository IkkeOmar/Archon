import { useState } from 'react';
import { FileCode, Copy, Check } from 'lucide-react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { useToast } from '../../contexts/ToastContext';

type RuleType = 'claude' | 'universal';

export const IDEGlobalRules = () => {
  const [copied, setCopied] = useState(false);
  const [selectedRuleType, setSelectedRuleType] = useState<RuleType>('claude');
  const { showToast } = useToast();
  
  const claudeRules = `# Archon-First Workflow (Claude)

Before coding, make sure:
- The FastAPI backend is running locally: `uv run python -m src.server.main`
- The UI is available at [http://localhost:3737](http://localhost:3737)
- Claude has network access to `http://127.0.0.1:8181` for REST calls

## Daily Flow
1. Open **Projects → Tasks** and review the current queue.
2. Research using **Knowledge Base → Search/Crawl** before implementing.
3. Track progress by moving tasks through **Todo → Doing → Review → Done** in the UI.
4. Document any follow-up work inside the task notes before closing.

## Claude Integration Notes
- Configure Claude’s custom tool to call the Archon REST API at `http://127.0.0.1:8181/api`.
- When Claude selects the Claude model in Archon, embeddings fall back to OpenAI—warn the user if no OpenAI key is present.
- Prefer smaller batches of requests; wait for the UI to show task state changes before sending the next command.

## Research Expectations
- Use the **Knowledge Base** view to surface relevant docs before requesting code changes.
- Summarize key findings back into the task or project PRD so humans can follow the reasoning.
- If the knowledge base lacks coverage, add sources or flag the gap for the team.`;

  const universalRules = `# Core Archon Workflow

Archon is the source of truth for tasks, knowledge, and project context.

## Standard Cycle
1. **Review Tasks** – Start in **Projects → Tasks** to understand priority and scope.
2. **Research** – Use **Knowledge Base** (crawl, upload, search) and note findings in the task.
3. **Implement** – Write code guided by research and project standards.
4. **Update Status** – Move tasks through **Todo → Doing → Review → Done** and log progress notes.
5. **Document** – Capture decisions, risks, and follow-ups in the task or PRD.

## Good Habits
- Keep Supabase credentials and provider keys up to date so tests and research succeed.
- Sync with teammates by leaving comments in the task timeline rather than external docs.
- When the backend restarts, refresh the UI to re-establish the Socket.IO connection.
- Always verify API responses locally (curl/Postman) before asking teammates to test.

Following this rhythm keeps Archon’s knowledge base accurate and ensures every change is traceable.`;
  const currentRules = selectedRuleType === 'claude' ? claudeRules : universalRules;

  // Simple markdown parser for display
  const renderMarkdown = (text: string) => {
    const lines = text.split('\n');
    const elements: JSX.Element[] = [];
    let inCodeBlock = false;
    let codeBlockContent: string[] = [];
    let codeBlockLang = '';
    const listStack: string[] = [];

    lines.forEach((line, index) => {
      // Code blocks
      if (line.startsWith('```')) {
        if (!inCodeBlock) {
          inCodeBlock = true;
          codeBlockLang = line.slice(3).trim();
          codeBlockContent = [];
        } else {
          inCodeBlock = false;
          elements.push(
            <pre key={index} className="bg-gray-900 dark:bg-gray-800 text-gray-100 p-3 rounded-md overflow-x-auto my-2">
              <code className="text-sm font-mono">{codeBlockContent.join('\n')}</code>
            </pre>
          );
        }
        return;
      }

      if (inCodeBlock) {
        codeBlockContent.push(line);
        return;
      }

      // Headers
      if (line.startsWith('# ')) {
        elements.push(<h1 key={index} className="text-2xl font-bold text-gray-800 dark:text-white mt-4 mb-2">{line.slice(2)}</h1>);
      } else if (line.startsWith('## ')) {
        elements.push(<h2 key={index} className="text-xl font-semibold text-gray-800 dark:text-white mt-3 mb-2">{line.slice(3)}</h2>);
      } else if (line.startsWith('### ')) {
        elements.push(<h3 key={index} className="text-lg font-semibold text-gray-800 dark:text-white mt-2 mb-1">{line.slice(4)}</h3>);
      }
      // Bold text
      else if (line.startsWith('**') && line.endsWith('**') && line.length > 4) {
        elements.push(<p key={index} className="font-semibold text-gray-700 dark:text-gray-300 my-1">{line.slice(2, -2)}</p>);
      }
      // Numbered lists
      else if (/^\d+\.\s/.test(line)) {
        const content = line.replace(/^\d+\.\s/, '');
        const processedContent = content
          .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
          .replace(/`([^`]+)`/g, '<code class="bg-gray-200 dark:bg-gray-700 px-1 py-0.5 rounded text-sm font-mono">$1</code>');
        elements.push(
          <li key={index} className="ml-6 list-decimal text-gray-600 dark:text-gray-400 my-0.5" 
              dangerouslySetInnerHTML={{ __html: processedContent }} />
        );
      }
      // Bullet lists (checking for both - and * markers, accounting for sublists)
      else if (/^(\s*)[-*]\s/.test(line)) {
        const indent = line.match(/^(\s*)/)?.[1].length || 0;
        const content = line.replace(/^(\s*)[-*]\s/, '');
        const processedContent = content
          .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
          .replace(/`([^`]+)`/g, '<code class="bg-gray-200 dark:bg-gray-700 px-1 py-0.5 rounded text-sm font-mono">$1</code>');
        const marginLeft = 6 + (indent * 2);
        elements.push(
          <li key={index} className={`ml-${marginLeft} list-disc text-gray-600 dark:text-gray-400 my-0.5`} 
              style={{ marginLeft: `${marginLeft * 4}px` }}
              dangerouslySetInnerHTML={{ __html: processedContent }} />
        );
      }
      // Inline code in regular text
      else if (line.includes('`') && !line.startsWith('`')) {
        const processedLine = line
          .replace(/`([^`]+)`/g, '<code class="bg-gray-200 dark:bg-gray-700 px-1 py-0.5 rounded text-sm font-mono">$1</code>');
        elements.push(
          <p key={index} className="text-gray-600 dark:text-gray-400 my-1" 
             dangerouslySetInnerHTML={{ __html: processedLine }} />
        );
      }
      // Empty lines
      else if (line.trim() === '') {
        elements.push(<div key={index} className="h-2" />);
      }
      // Regular text
      else {
        elements.push(<p key={index} className="text-gray-600 dark:text-gray-400 my-1">{line}</p>);
      }
    });

    return elements;
  };

  const handleCopyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(currentRules);
      setCopied(true);
      showToast(`${selectedRuleType === 'claude' ? 'Claude Code' : 'Universal'} rules copied to clipboard!`, 'success');
      
      // Reset copy icon after 2 seconds
      setTimeout(() => {
        setCopied(false);
      }, 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
      showToast('Failed to copy to clipboard', 'error');
    }
  };

  return (
    <Card accentColor="blue" className="p-8">
      <div className="space-y-6">
        <div className="flex justify-between items-start">
          <p className="text-sm text-gray-600 dark:text-zinc-400 w-4/5">
            Add global rules to your AI assistant to ensure consistent Archon workflow integration.
          </p>
          <Button 
            variant="outline" 
            accentColor="blue" 
            icon={copied ? <Check className="w-4 h-4 mr-1" /> : <Copy className="w-4 h-4 mr-1" />}
            className="ml-auto whitespace-nowrap px-4 py-2"
            size="md"
            onClick={handleCopyToClipboard}
          >
            {copied ? 'Copied!' : `Copy ${selectedRuleType === 'claude' ? 'Claude Code' : 'Universal'} Rules`}
          </Button>
        </div>

        {/* Rule Type Selector */}
        <fieldset className="flex items-center space-x-6">
          <legend className="sr-only">Select rule type</legend>
          <label className="flex items-center cursor-pointer">
            <input
              type="radio"
              name="ruleType"
              value="claude"
              checked={selectedRuleType === 'claude'}
              onChange={() => setSelectedRuleType('claude')}
              className="mr-2 text-blue-500 focus:ring-blue-500"
              aria-label="Claude Code Rules - Comprehensive Archon workflow instructions for Claude"
            />
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Claude Code Rules</span>
          </label>
          <label className="flex items-center cursor-pointer">
            <input
              type="radio"
              name="ruleType"
              value="universal"
              checked={selectedRuleType === 'universal'}
              onChange={() => setSelectedRuleType('universal')}
              className="mr-2 text-blue-500 focus:ring-blue-500"
              aria-label="Universal Agent Rules - Simplified workflow for all other AI agents"
            />
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Universal Agent Rules</span>
          </label>
        </fieldset>

        <div className="border border-blue-200 dark:border-blue-800/30 bg-gradient-to-br from-blue-500/10 to-blue-600/10 backdrop-blur-sm rounded-md h-[400px] flex flex-col">
          <div className="p-4 pb-2 border-b border-blue-200/50 dark:border-blue-800/30">
            <h3 className="text-base font-semibold text-gray-800 dark:text-white">
              {selectedRuleType === 'claude' ? 'Claude Code' : 'Universal Agent'} Rules
            </h3>
          </div>
          <div className="flex-1 overflow-y-auto p-4 custom-scrollbar">
            <div className="prose prose-sm dark:prose-invert max-w-none">
              {renderMarkdown(currentRules)}
            </div>
          </div>
        </div>

        {/* Info Note */}
        <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-md">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            <strong>Where to place these rules:</strong>
          </p>
          <ul className="text-sm text-gray-600 dark:text-gray-400 mt-2 ml-4 list-disc">
            <li><strong>Claude Code:</strong> Create a CLAUDE.md file in your project root</li>
            <li><strong>Cursor:</strong> Create .cursorrules file or add to Settings → Rules</li>
            <li><strong>Windsurf:</strong> Create .windsurfrules file in project root</li>
            <li><strong>Other IDEs:</strong> Add to your IDE's AI assistant configuration</li>
          </ul>
        </div>
      </div>
    </Card>
  );
};
