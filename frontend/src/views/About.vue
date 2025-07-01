<template>
  <v-container>
    <v-row>
      <v-col cols="12" md="8" offset-md="2">
        <v-card class="mt-4">
          <v-img
            src="https://images.unsplash.com/photo-1507842217343-583bb7270b66?ixlib=rb-1.2.1&auto=format&fit=crop&w=1000&q=80"
            height="200"
            cover
          >
            <template v-slot:placeholder>
              <v-row
                class="fill-height ma-0"
                align="center"
                justify="center"
              >
                <v-progress-circular
                  indeterminate
                  color="grey-lighten-5"
                ></v-progress-circular>
              </v-row>
            </template>
          </v-img>

          <v-card-title class="text-h4 d-flex align-center">
            <v-icon start size="large" color="primary">mdi-information</v-icon>
            About arXiv RSS Filter Bot
          </v-card-title>

          <v-card-text>
            <p class="text-body-1 mb-4">
              The arXiv RSS Filter Bot is a powerful tool that helps researchers stay up-to-date with the latest 
              research papers in their field of interest. The bot filters papers from arXiv based on user-defined 
              keywords and date ranges, generating a personalized RSS feed.
            </p>
            
            <h3 class="text-h5 mb-3">Key Features</h3>
            <v-list>
              <v-list-item>
                <template v-slot:prepend>
                  <v-icon color="primary">mdi-arrow-right-circle</v-icon>
                </template>
                <v-list-item-title>Automated paper fetching from arXiv</v-list-item-title>
                <v-list-item-subtitle>
                  Retrieve the latest papers from your chosen arXiv categories
                </v-list-item-subtitle>
              </v-list-item>
              
              <v-list-item>
                <template v-slot:prepend>
                  <v-icon color="primary">mdi-arrow-right-circle</v-icon>
                </template>
                <v-list-item-title>Keyword-based filtering</v-list-item-title>
                <v-list-item-subtitle>
                  Filter papers by user-defined keywords that match your research interests
                </v-list-item-subtitle>
              </v-list-item>
              
              <v-list-item>
                <template v-slot:prepend>
                  <v-icon color="primary">mdi-arrow-right-circle</v-icon>
                </template>
                <v-list-item-title>Date-based filtering</v-list-item-title>
                <v-list-item-subtitle>
                  Filter papers by recency or specific year/month
                </v-list-item-subtitle>
              </v-list-item>
              
              <v-list-item>
                <template v-slot:prepend>
                  <v-icon color="primary">mdi-arrow-right-circle</v-icon>
                </template>
                <v-list-item-title>Author and institution extraction</v-list-item-title>
                <v-list-item-subtitle>
                  View author names and their affiliated institutions
                </v-list-item-subtitle>
              </v-list-item>
              
              <v-list-item>
                <template v-slot:prepend>
                  <v-icon color="primary">mdi-arrow-right-circle</v-icon>
                </template>
                <v-list-item-title>RSS feed generation</v-list-item-title>
                <v-list-item-subtitle>
                  Create standard RSS feeds compatible with any feed reader
                </v-list-item-subtitle>
              </v-list-item>
              
              <v-list-item>
                <template v-slot:prepend>
                  <v-icon color="primary">mdi-arrow-right-circle</v-icon>
                </template>
                <v-list-item-title>Scheduled running</v-list-item-title>
                <v-list-item-subtitle>
                  Configure the bot to run automatically at specified times
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>
            
            <h3 class="text-h5 mb-3 mt-6">How It Works</h3>
            <p class="text-body-1 mb-2">The bot follows these steps to generate your personalized feed:</p>
            <ol class="mb-4">
              <li class="mb-2">Fetches the latest papers from your configured arXiv categories</li>
              <li class="mb-2">Filters the papers based on your keywords</li>
              <li class="mb-2">Applies date filtering to focus on recent or specific time periods</li>
              <li class="mb-2">Extracts author and institution information</li>
              <li class="mb-2">Generates an RSS feed with the filtered papers</li>
            </ol>
            
            <h3 class="text-h5 mb-3 mt-6">Getting Started</h3>
            <p class="text-body-1 mb-2">To get started with the arXiv RSS Filter Bot:</p>
            <ol>
              <li class="mb-2">Go to the <router-link to="/config">Configuration</router-link> page to set up your keywords and preferences</li>
              <li class="mb-2">Select the arXiv categories relevant to your research</li>
              <li class="mb-2">Configure filtering parameters like maximum days old or specific date ranges</li>
              <li class="mb-2">Go to the <router-link to="/">Dashboard</router-link> and click "Run Now" to generate your feed</li>
              <li class="mb-2">View and share your personalized RSS feed from the <router-link to="/feeds">Feeds</router-link> page</li>
            </ol>
            
            <h3 class="text-h5 mb-3 mt-6">Technology Stack</h3>
            <v-chip-group>
              <v-chip variant="outlined" color="primary">Python</v-chip>
              <v-chip variant="outlined" color="primary">Vue.js</v-chip>
              <v-chip variant="outlined" color="primary">Vuetify</v-chip>
              <v-chip variant="outlined" color="primary">Flask</v-chip>
              <v-chip variant="outlined" color="primary">RSS</v-chip>
              <v-chip variant="outlined" color="primary">arXiv API</v-chip>
            </v-chip-group>
          </v-card-text>

          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              variant="tonal"
              color="primary"
              prepend-icon="mdi-github"
              href="https://github.com/yourusername/arxiv-rss-filter-bot"
              target="_blank"
            >
              GitHub Repository
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: 'AboutView'
}
</script>