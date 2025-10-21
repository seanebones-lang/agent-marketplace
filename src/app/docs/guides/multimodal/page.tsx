import { GenericDocPage } from '@/components/docs/GenericDocPage'

export default function MultimodalPage() {
  return (
    <GenericDocPage
      title="Multi-Modal Processing"
      category="Guides"
      description="Leverage text, image, and voice processing capabilities in your agents"
      content={{
        sections: [
          {
            title: "Overview",
            content: "Multi-modal agents can process multiple types of input simultaneously - text, images, audio, and video. This enables richer context understanding and more accurate results. Our platform supports Claude 3.5 Sonnet, GPT-4 Vision, and Whisper v3 for comprehensive multi-modal capabilities."
          },
          {
            title: "Text + Image Processing",
            content: (
              <div className="space-y-4">
                <p className="text-gray-700 dark:text-gray-300">
                  Analyze images alongside text for enhanced context:
                </p>
                <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                  <code>{`result = client.execute_agent(
    agent_id="multimodal-analyzer",
    input_data={
        "text": "Analyze this UI for accessibility issues",
        "images": [
            {"url": "https://example.com/screenshot.png"},
            {"base64": "iVBORw0KGgoAAAANSUhEUg..."}
        ]
    }
)`}</code>
                </pre>
              </div>
            )
          },
          {
            title: "Voice Processing",
            content: (
              <div className="space-y-4">
                <p className="text-gray-700 dark:text-gray-300">
                  Transcribe and analyze audio input:
                </p>
                <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                  <code>{`result = client.execute_agent(
    agent_id="voice-analyzer",
    input_data={
        "audio_url": "https://example.com/recording.mp3",
        "language": "en",
        "analyze_sentiment": True
    }
)`}</code>
                </pre>
              </div>
            )
          },
          {
            title: "Use Cases",
            content: (
              <ul className="list-disc pl-6 space-y-2 text-gray-700 dark:text-gray-300">
                <li><strong>Document Analysis:</strong> Extract data from scanned documents and images</li>
                <li><strong>UI/UX Review:</strong> Analyze screenshots for design and accessibility issues</li>
                <li><strong>Customer Support:</strong> Process voice calls and chat screenshots</li>
                <li><strong>Content Moderation:</strong> Analyze images and text for policy violations</li>
                <li><strong>Medical Imaging:</strong> Analyze medical images with clinical context</li>
              </ul>
            )
          }
        ]
      }}
    />
  )
}

