import SwiftUI

struct ChatBubble: View {
    let message: ChatMessage

    var body: some View {
        HStack {
            if message.isUser { Spacer() }

            VStack(alignment: .leading, spacing: 4) {
                Text(message.text)
                    .padding()
                    .background(message.isUser ? Color.blue : Color.gray.opacity(0.2))
                    .foregroundColor(message.isUser ? .white : .black)
                    .cornerRadius(16)

                HStack {
                    Text(message.timestamp, style: .time)
                        .font(.caption2)
                        .foregroundColor(.gray)
                    
                    if let provider = message.provider {
                        Text("[\(provider)]")
                            .font(.caption2)
                            .foregroundColor(.purple)
                    }
                }
            }

            if !message.isUser { Spacer() }
        }
        .padding(message.isUser ? .leading : .trailing, 50)
        .padding(.vertical, 4)
    }
}
