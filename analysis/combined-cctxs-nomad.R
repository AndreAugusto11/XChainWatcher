library(ggplot2)
library(scales)

format_seconds_to_days <- function(seconds) {
  if (is.na(seconds)) return(NA)
  
  if (seconds >= 86400) {
    days <- seconds / 86400
    sprintf("%s\n(%.2f days)", 
            scales::comma(seconds), 
            days)
  } else if (seconds >= 3600) {
    hours <- seconds / 3600
    sprintf("%s\n(%.2f hours)", 
            scales::comma(seconds), 
            hours)
  } else if (seconds >= 60) {
    mins <- seconds / 60
    sprintf("%s\n(%.2f minutes)", 
            scales::comma(seconds), 
            mins)
  } else {
    # Just format seconds with commas
    scales::comma(seconds)
  }
}

df <- read.csv("cross-chain-rules-validator/analysis/nomad-bridge/data/combined_cctxs.csv")

p <- ggplot(df, aes(x = time_difference, y = value_usd, color = action)) +
  geom_point(size = 1, alpha = 0.7) +
  geom_vline(xintercept = 1800, linetype = "dashed", color = "black", size = 0.5) +
  annotate("text", 3000, 10000000000, hjust = .5, label = "Finality Time (30 mins)", colour = "black") +
  scale_color_manual(breaks = c("withdrawal", "deposit"), labels = c("CCTX_ValidWithdrawal", "CCTX_ValidDeposit"), values = c("royalblue3", "magenta")) +
  scale_x_log10(
    limits = c(10^3, NA),
    labels = function(x) {
      # Apply the custom formatting function to each tick mark
      sapply(x, format_seconds_to_days)
    }
  ) +
  scale_y_log10(
    limits = c(10^-7, 10^10),
    breaks = scales::trans_breaks(log10, function(x) 10^x, 10),
    labels = function(x) {
      ifelse(x < 1, 
             scales::dollar_format(accuracy = 0.000001)(x),
             scales::dollar_format()(x))
    }
  ) +
  labs(title = "CCTX Latency vs. CCTX Value Transferred (Nomad Bridge)",
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
    legend.position = c(0.82, 0.15),
    legend.background = element_rect(fill="lightblue",
                                     size=0.5, linetype="solid", color="lightblue")
  ) 

print(p)

# ggsave("analysis/figures/combined_cctxs.pdf", p, width = 10, height = 8)