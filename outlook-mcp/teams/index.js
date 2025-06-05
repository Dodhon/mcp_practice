/**
 * Teams module for Outlook MCP server
 */
const handleListTeams = require('./list-teams');
const handleListChannels = require('./list-channels');
const handleSendChannelMessage = require('./send-channel-message');
const handleReadChannelMessages = require('./read-channel-messages');

// Teams tool definitions
const teamsTools = [
  {
    name: "teams-list-teams",
    description: "Lists all Microsoft Teams that the user has access to",
    inputSchema: {
      type: "object",
      properties: {
        count: {
          type: "number",
          description: "Number of teams to retrieve (default: 25, max: 50)"
        }
      },
      required: []
    },
    handler: handleListTeams
  },
  {
    name: "teams-list-channels",
    description: "Lists channels in a specific Microsoft Team",
    inputSchema: {
      type: "object",
      properties: {
        teamId: {
          type: "string",
          description: "ID of the team to list channels for"
        },
        channelType: {
          type: "string",
          description: "Filter by channel type (standard, private, shared)",
          enum: ["standard", "private", "shared"]
        }
      },
      required: ["teamId"]
    },
    handler: handleListChannels
  },
  {
    name: "teams-send-channel-message",
    description: "Sends a message to a Microsoft Teams channel",
    inputSchema: {
      type: "object",
      properties: {
        teamId: {
          type: "string",
          description: "ID of the team containing the channel"
        },
        channelId: {
          type: "string",
          description: "ID of the channel to send message to"
        },
        message: {
          type: "string",
          description: "Message content to send"
        },
        contentType: {
          type: "string",
          description: "Content type of the message (text or html)",
          enum: ["text", "html"],
          default: "text"
        }
      },
      required: ["teamId", "channelId", "message"]
    },
    handler: handleSendChannelMessage
  },
  {
    name: "teams-read-channel-messages",
    description: "Reads recent messages from a Microsoft Teams channel",
    inputSchema: {
      type: "object",
      properties: {
        teamId: {
          type: "string",
          description: "ID of the team containing the channel"
        },
        channelId: {
          type: "string",
          description: "ID of the channel to read messages from"
        },
        count: {
          type: "number",
          description: "Number of messages to retrieve (default: 20, max: 50)"
        }
      },
      required: ["teamId", "channelId"]
    },
    handler: handleReadChannelMessages
  }
];

module.exports = {
  teamsTools,
  handleListTeams,
  handleListChannels,
  handleSendChannelMessage,
  handleReadChannelMessages
}; 