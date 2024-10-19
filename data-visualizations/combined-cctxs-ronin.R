library(ggplot2)
library(scales)

format_seconds_to_days <- function(seconds) {
  if (is.na(seconds)) return(NA)
  
  if (seconds >= 86400) {  # 86400 seconds in a day
    # Convert seconds to days
    days <- seconds / 86400
    sprintf("%s\n(%.2f days)", 
            scales::comma(seconds), 
            days)
  } else if (seconds >= 3600) {  # 3600 seconds in an hour
    # Convert seconds to hours
    hours <- seconds / 3600
    sprintf("%s\n(%.2f hours)", 
            scales::comma(seconds), 
            hours)
  } else if (seconds >= 60) {  # 3600 seconds in an hour
    # Convert seconds to hours
    mins <- seconds / 60
    sprintf("%s\n(%.2f minutes)", 
            scales::comma(seconds), 
            mins)
  } else {
    # Just format seconds with commas
    scales::comma(seconds)
  }
}

df <- read.csv('../cross-chain-rules-validator/analysis/ronin-bridge/data/combined_cctxs.csv')

df <- df[order(df$action, decreasing=TRUE), ]
df <- df[df$value_usd > 0.000001, ]

p <- ggplot(df, aes(x = time_difference, y = value_usd, color = action)) +
  geom_point(size = 1, alpha = 0.7) +
  geom_vline(xintercept = 78, linetype = "dashed", color = "magenta", size = 0.5) +
  geom_vline(xintercept = 45, linetype = "dashed", color = "royalblue3", size = 0.5) +
  annotate("text", 100, 10000000000, hjust = .5, label = "Finality Times (45 & 78 seconds)", colour = "black") +
  scale_color_manual(breaks = c("withdrawal", "deposit"), labels = c("CCTX_ValidWithdrawal", "CCTX_ValidDeposit"), values = c("royalblue3", "magenta")) +
  scale_x_log10(
    limits = c(10^1, NA),
    labels = function(x) {
      # Apply the custom formatting function to each tick mark
      sapply(x, format_seconds_to_days)
    }
  ) +            # Set the lower limit of the x-axis to 10^3, NA allows for an upper limit based on data
  scale_y_log10(
    breaks = scales::trans_breaks(log10, function(x) 10^x, 10),
    labels = function(x) {
      ifelse(x < 1, 
             scales::dollar_format(accuracy = 0.000001)(x),  # Maintains two decimal places for values < 1
             scales::dollar_format()(x))                 # Default formatting for values >= 1
    }
  ) +
  labs(title = "CCTX Latency vs. CCTX Value Transferred (Ronin Bridge)",
       x = "CCTX Latency (seconds)",
       y = "CCTX Value (USD)",
       color = "Datalog Rule") +
  theme_minimal() +
  theme(
    text = element_text(family = "serif"),
    axis.line = element_line(colour = "black"),
    plot.title = element_text(face = "bold", size = 15, hjust = 0.5, vjust=1),
    panel.grid.major.y = element_line(color = 4,
                                      size = 0.1,
                                      linetype = 2),
    panel.grid.major.x = element_line(color = 4,
                                      size = 0.1,
                                      linetype = 2),
    panel.grid.minor.x = element_blank(),
    panel.grid.minor.y = element_blank(),
    axis.title.y=element_text(size=14, face="bold", vjust=-2),
    axis.title.x=element_text(size=14, face="bold", vjust=-1),
    legend.title = element_text(face = "bold", size=14),
    legend.text = element_text(size = 10, family = "mono"),
    axis.title = element_text(size = 13), 
    axis.text = element_text(size = 13, face="bold"),
    legend.position = c(0.81, 0.15),
    legend.background = element_rect(fill="lightblue",
                                     size=0.5, linetype="solid", color="lightblue")
  ) 

print(p)
