import { useMemo, useState } from "react";
import { Key, ExternalLink, Save, Loader } from "lucide-react";
import { Input } from "../ui/Input";
import { Button } from "../ui/Button";
import { Select } from "../ui/Select";
import { useToast } from "../../contexts/ToastContext";
import { credentialsService } from "../../services/credentialsService";

interface ProviderStepProps {
  onSaved: () => void;
  onSkip: () => void;
}

type SupportedProvider = "openai" | "google" | "anthropic";

interface ProviderConfig {
  label: string;
  description: string;
  docsUrl: string;
  apiKeyExample: string;
  apiKeyLabel: string;
  credentialKey: string;
  defaultModel: string;
}

const PROVIDERS: Record<SupportedProvider, ProviderConfig> = {
  openai: {
    label: "OpenAI",
    description: "Use GPT-4.1 or GPT-4o family models for fast, general-purpose reasoning.",
    docsUrl: "https://platform.openai.com/api-keys",
    apiKeyExample: "sk-proj-...",
    apiKeyLabel: "OpenAI API Key",
    credentialKey: "OPENAI_API_KEY",
    defaultModel: "gpt-4.1-mini",
  },
  google: {
    label: "Google Gemini",
    description: "Run Google's Gemini models through the AI Studio OpenAI-compatible API.",
    docsUrl: "https://aistudio.google.com/app/apikey",
    apiKeyExample: "AIza...",
    apiKeyLabel: "Google API Key",
    credentialKey: "GOOGLE_API_KEY",
    defaultModel: "gemini-1.5-flash",
  },
  anthropic: {
    label: "Claude (Anthropic)",
    description: "Access Claude 3 models for high-quality reasoning and code assistance.",
    docsUrl: "https://console.anthropic.com/settings/keys",
    apiKeyExample: "sk-ant-...",
    apiKeyLabel: "Anthropic API Key",
    credentialKey: "ANTHROPIC_API_KEY",
    defaultModel: "claude-3-5-sonnet-latest",
  },
};

export const ProviderStep = ({ onSaved, onSkip }: ProviderStepProps) => {
  const [provider, setProvider] = useState<SupportedProvider>("openai");
  const [apiKey, setApiKey] = useState("");
  const [saving, setSaving] = useState(false);
  const { showToast } = useToast();

  const providerConfig = useMemo(() => PROVIDERS[provider], [provider]);

  const handleSave = async () => {
    if (!apiKey.trim()) {
      showToast("Please enter an API key", "error");
      return;
    }

    setSaving(true);
    try {
      // Save the selected provider API key
      await credentialsService.updateCredential({
        key: providerConfig.credentialKey,
        value: apiKey,
        is_encrypted: true,
        category: "api_keys",
      });

      // Persist the provider and default model so the backend can use it immediately
      await Promise.all([
        credentialsService.updateCredential({
          key: "LLM_PROVIDER",
          value: provider,
          is_encrypted: false,
          category: "rag_strategy",
        }),
        credentialsService.updateCredential({
          key: "MODEL_CHOICE",
          value: providerConfig.defaultModel,
          is_encrypted: false,
          category: "rag_strategy",
        }),
      ]);

      showToast(`${providerConfig.label} connected successfully!`, "success");
      // Mark onboarding as dismissed when API key is saved
      localStorage.setItem("onboardingDismissed", "true");
      onSaved();
    } catch (error) {
      // Log error for debugging per alpha principles
      const errorMessage =
        error instanceof Error ? error.message : "Unknown error";
      console.error("Failed to save API key:", error);

      // Show specific error details to help user resolve the issue
      if (errorMessage.includes("network") || errorMessage.includes("fetch")) {
        showToast(
          `Network error while saving API key: ${errorMessage}. Please check your connection.`,
          "error",
        );
      } else {
        // Show the actual error for unknown issues
        showToast(`Failed to save API key: ${errorMessage}`, "error");
      }
    } finally {
      setSaving(false);
    }
  };

  const handleSkip = () => {
    showToast("You can configure your provider in Settings", "info");
    // Mark onboarding as dismissed when skipping
    localStorage.setItem("onboardingDismissed", "true");
    onSkip();
  };

  return (
    <div className="space-y-6">
      {/* Provider Selection */}
      <div>
        <Select
          label="Select AI Provider"
          value={provider}
          onChange={(e) => {
            const value = e.target.value as SupportedProvider;
            setProvider(value);
            setApiKey("");
          }}
          options={[
            { value: "openai", label: "OpenAI" },
            { value: "google", label: "Google Gemini" },
            { value: "anthropic", label: "Claude (Anthropic)" },
          ]}
          accentColor="green"
        />
        <p className="mt-2 text-sm text-gray-600 dark:text-zinc-400">
          {providerConfig.description}
        </p>
      </div>

      <div>
        <Input
          label={providerConfig.apiKeyLabel}
          type="password"
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
          placeholder={providerConfig.apiKeyExample}
          accentColor="green"
          icon={<Key className="w-4 h-4" />}
        />
        <p className="mt-2 text-sm text-gray-600 dark:text-zinc-400">
          Keys are encrypted locally before being stored in Archon's credentials vault.
        </p>
      </div>

      <div className="flex items-center gap-2 text-sm">
        <a
          href={providerConfig.docsUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-500 hover:text-blue-600 dark:text-blue-400 dark:hover:text-blue-300 flex items-center gap-1"
        >
          Get an API key from {providerConfig.label}
          <ExternalLink className="w-3 h-3" />
        </a>
      </div>

      <div className="flex gap-3 pt-4">
        <Button
          variant="primary"
          size="lg"
          onClick={handleSave}
          disabled={saving || !apiKey.trim()}
          icon={
            saving ? (
              <Loader className="w-4 h-4 animate-spin" />
            ) : (
              <Save className="w-4 h-4" />
            )
          }
          className="flex-1"
        >
          {saving ? "Saving..." : "Save & Continue"}
        </Button>
        <Button
          variant="outline"
          size="lg"
          onClick={handleSkip}
          disabled={saving}
          className="flex-1"
        >
          Skip for Now
        </Button>
      </div>
    </div>
  );
};
