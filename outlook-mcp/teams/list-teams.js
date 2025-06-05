/**
 * List Teams handler
 */
const { callGraphAPI } = require('../utils/graph-api');
const { ensureAuthenticated } = require('../auth');

async function handleListTeams(args) {
  try {
    const { count = 25 } = args;
    
    // Validate count parameter
    if (count > 50) {
      throw new Error('Count cannot exceed 50');
    }

    // Get access token
    const accessToken = await ensureAuthenticated();
    
    // Get user's teams
    const response = await callGraphAPI(accessToken, 'GET', 'me/joinedTeams', null, { $top: count });

    const teams = response.value.map(team => ({
      id: team.id,
      displayName: team.displayName,
      description: team.description || '',
      webUrl: team.webUrl,
      isArchived: team.isArchived || false,
      visibility: team.visibility,
      createdDateTime: team.createdDateTime,
      memberSettings: {
        allowCreatePrivateChannels: team.memberSettings?.allowCreatePrivateChannels,
        allowCreateUpdateChannels: team.memberSettings?.allowCreateUpdateChannels,
        allowDeleteChannels: team.memberSettings?.allowDeleteChannels
      }
    }));

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            success: true,
            count: teams.length,
            teams: teams
          }, null, 2)
        }
      ]
    };

  } catch (error) {
    console.error('Error listing teams:', error);
    
    if (error.message === 'Authentication required') {
      return {
        content: [{ 
          type: "text", 
          text: "Authentication required. Please use the 'authenticate' tool first."
        }]
      };
    }
    
    let errorMessage = 'Failed to list teams';
    if (error.message.includes('403')) {
      errorMessage = 'Insufficient permissions to list teams. Please ensure the application has Team.ReadBasic.All permission.';
    } else if (error.message.includes('401')) {
      errorMessage = 'Authentication failed. Please ensure you are logged in.';
    } else if (error.message) {
      errorMessage = error.message;
    }

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            success: false,
            error: errorMessage
          }, null, 2)
        }
      ]
    };
  }
}

module.exports = handleListTeams; 