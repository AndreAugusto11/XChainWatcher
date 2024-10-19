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
  } else {
    scales::comma(seconds)
  }
}

df <- read.csv('../cross-chain-rules-validator/analysis/ronin-bridge/data/cctxs_deposits-with-finality-break.csv')
df <- df[df$value_usd > 0.000001, ]

print(nrow(df[df$time_difference < 78, ]))

p <- ggplot(df, aes(x = time_difference, y = value_usd)) +
  geom_point(size = 1, alpha = 0.7, aes(color = time_difference > 78)) +
  geom_vline(xintercept = 78, linetype = "dashed", color = "black", size = 0.5) +
  annotate("text", 10, 1000000000, hjust = .5, label = "Ethereum Finality Time (78 seconds)", colour = "black") +
  scale_color_manual(labels = c("Unmatched SC_ValidNativeTokenDeposit", "CCTX_ValidDeposit"), values = c("black", "magenta")) +
  #annotate("point", x = 125, y = 100, size = 30, shape = 21, color = "red", fill = NA, stroke = 0.5) +
  scale_x_log10(limits = c(1, 10000), breaks = scales::trans_breaks("log10", function(x) 10^x, 5),) +
  scale_y_log10(
    breaks = scales::trans_breaks("log10", function(x) 10^x, 10),
    labels = function(x) {
      ifelse(x < 1, 
             scales::dollar_format(accuracy = 0.000001)(x),  # Maintains two decimal places for values < 1
             scales::dollar_format()(x))                 # Default formatting for values >= 1
    }
  ) +
  labs(title = "Ethereum Finality Violation (Deposits in the Ronin Bridge)",
       x = "CCTX Latency (seconds)",
       y = "CCTX Value (USD)",
       color = "") +
  theme_minimal() +
  theme(
    plot.margin = unit(c(0.1, 0.5, 0, 0), "cm"),
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
    legend.text = element_text(size = 13, family = "mono"),
    axis.title = element_text(size = 13), 
    axis.text = element_text(size = 13, face="bold"),
    legend.position = "bottom"
  ) 

print(p)
#output latency_vs_value_finality_break_dep_ronin


df <- read.csv('../cross-chain-rules-validator/analysis/ronin-bridge/data/cctxs_withdrawals-with-finality-break.csv')
print(nrow(df[df$time_difference < 45, ]))

p <- ggplot(df, aes(x = time_difference, y = value_usd)) +
  geom_point(size = 1, alpha = 0.7, aes(color = time_difference > 45)) +
  geom_vline(xintercept = 45, linetype = "dashed", color = "red", size = 0.5) +
  annotate("text", 6, 1000000000, hjust = .5, label = "Ronin Finality Time (45 seconds)", colour = "red") +
  scale_color_manual(labels = c("Unmatched TC_ValidERC20TokenWithdrawal", "CCTX_ValidWithdrawal"), values = c("red", "royalblue3")) +
  scale_x_log10(limits = c(1, 10000), breaks = scales::trans_breaks("log10", function(x) 10^x, 5),) +
  scale_y_log10(
    breaks = scales::trans_breaks("log10", function(x) 10^x, 10),
    labels = function(x) {
      ifelse(x < 1, 
             scales::dollar_format(accuracy = 0.000001)(x),  # Maintains two decimal places for values < 1
             scales::dollar_format()(x))                 # Default formatting for values >= 1
    }
  ) +
  labs(title = "Ronin Finality Violation (Withdrawals in the Ronin Bridge)",
       x = "CCTX Latency (seconds)",
       y = "CCTX Value (USD)",
       color = "") +
  theme_minimal() +
  theme(
    plot.margin = unit(c(0.1, 0.5, 0, 0), "cm"),
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
    legend.text = element_text(size = 13, family = "mono"),
    axis.title = element_text(size = 13), 
    axis.text = element_text(size = 13, face="bold"),
    legend.position = "bottom"
  ) 

print(p)

#output latency_vs_value_finality_break_with_ronin
