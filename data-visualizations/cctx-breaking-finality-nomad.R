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
    sprintf("%s\n(%.2f mins)", 
            scales::comma(seconds), 
            mins)
    scales::comma(seconds)
  }
}

data <- read.csv("../cross-chain-rules-validator/analysis/nomad-bridge/data/cctxs_deposits-with-finality-break.csv")

data_before <- merged_df %>%
  filter((bridge == "ronin" & timestamp < 1648508400) |
           (bridge == "nomad" & timestamp < 1659389551))

p <- ggplot(data_before, aes(x = time_difference, y = value_usd)) +
  geom_point(size = 1, alpha = 0.7, aes(color = time_difference > 1800)) +
  geom_vline(xintercept = 1800, linetype = "dashed", color = "black", size = 0.5) +
  scale_color_manual(labels = c("Unmatched SC_ValidERC20TokenDeposit", "CCTX_ValidDeposit"), values = c("red", "magenta")) +
  annotate("text", 3000, 50000000, hjust = .5, label = "Fraud Proof Window Time (30 mins)", colour = "black") +
  annotate("point", x = 125, y = 100, size = 30, shape = 21, color = "red", fill = NA, stroke = 0.5) +
  annotate("text", 250, 200000, hjust = .5, label = "5 invalid CCTXs accepted\nby the Nomad Bridge", colour = "red") +
  scale_x_log10(
    breaks = scales::trans_breaks("log10", function(x) 10^x),
    labels = function(x) {
      sapply(x, format_seconds_to_days)
    }
  ) +
  scale_y_log10(
    breaks = scales::trans_breaks("log10", function(x) 10^x),
    labels = function(x) {
      ifelse(x < 1, 
             scales::dollar_format(accuracy = 0.0001)(x),
             scales::dollar_format()(x))
    }
  ) +
  labs(title = "Fraud Proof Window Violation (Deposits in the Nomad Bridge)",
       x = "CCTX Latency (seconds)",
       y = "CCTX Value (USD)",
       color = "") +
  theme_minimal() +
  theme(
    plot.margin = unit(c(0.1, 0.5, 0, 0), "cm"),
    text = element_text(family = "serif"),
    axis.line = element_line(colour = "black"),
    plot.title = element_text(face = "bold", size = 15, hjust = 0.5, vjust=1),
    panel.grid.major.y = element_line(color = 4, size = 0.1, linetype = 2),
    panel.grid.major.x = element_line(color = 4, size = 0.1, linetype = 2),
    panel.grid.minor.x = element_blank(),
    panel.grid.minor.y = element_blank(),
    axis.title.y = element_text(size=14, face="bold", vjust=-2),
    axis.title.x = element_text(size=14, face="bold", vjust=-1),
    legend.title = element_text(face = "bold", size=14),
    legend.text = element_text(size = 13, family = "mono"),
    axis.title = element_text(size = 13), 
    axis.text = element_text(size = 13, face="bold"),
    legend.position = "bottom"
  ) 

print(p)

#ggsave("analysis/figures/latency_vs_value_finality_break_nomad.pdf", p, width = 10, height = 8)