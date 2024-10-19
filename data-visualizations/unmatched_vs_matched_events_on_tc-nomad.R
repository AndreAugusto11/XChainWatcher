library(ggplot2)
library(scales)
library(lubridate)
library(dplyr)

df <- read.csv("../cross-chain-rules-validator/analysis/nomad-bridge/data/matched_and_unmatched_tc_withdrawals.csv")

df <- df %>% 
  mutate(
    value_mil = value_usd/10^6,
    date = as.POSIXct(date, format="%Y-%m-%d %H:%M:%S", tz="UTC"),
    interval = floor_date(date, "6 hours")
  )

df_matched <- df %>% 
  filter(matched == "True") %>%
  group_by(interval) %>%
  summarise(total_count = n(), value = sum(value_mil)) %>%
  mutate(matched = "Matched")

df_unmatched <- df %>% 
  filter(matched == "False") %>%
  group_by(interval) %>%
  summarise(total_count = n(), value = sum(value_mil)) %>%
  mutate(matched = "Unmatched")

merged_df <- bind_rows(df_matched, df_unmatched)

p <- ggplot(merged_df, aes(x=interval, y=total_count, size=value, color=matched)) + 
  geom_point(alpha=0.6) +
  scale_size_continuous(range = c(2, 11), breaks=c(1, 5, 10, 15, 20), labels = c("$1M", "$5M", "$10M", "$15M", "$20M"), name="Transferred Value (USD)") +
  scale_color_manual(values=c("royalblue3", "red")) +
  scale_x_datetime(limits = as.POSIXct(c("2022-01-01", "2022-08-05"), tz="UTC"), 
                   date_labels="%Y-%m", date_breaks="2 month") +
  scale_y_continuous(breaks = seq(0, 300, 50)) +
  labs(title = "Matched vs. Unmatched Withdrawal Events in T (Nomad Bridge)",
       x = "Date",
       y = "Number of Events",
       color = "") +
  theme_minimal() +
  theme(
    plot.margin = unit(c(0, 0, 0, 0), "cm"),
    text = element_text(family = "serif"),
    axis.line = element_line(colour = "black", linewidth = 0.5),
    panel.grid.major.y = element_line(color = 4, linewidth = 0.1, linetype = 2),
    panel.grid.major.x = element_line(color = 4, linewidth = 0.1, linetype = 2),
    plot.title = element_text(face = "bold", size = 15, hjust = 0.5, vjust=1),
    panel.grid.minor.x = element_blank(),
    panel.grid.minor.y = element_blank(),
    axis.title.y = element_text(size=14, face="bold"),
    axis.title.x = element_text(size=14, face="bold"),
    legend.title = element_text(face = "bold", size=14),
    legend.text = element_text(size = 13, family = "mono"),
    axis.title = element_text(size = 13), 
    axis.text = element_text(size = 13, face="bold"),
  ) 

print(p)

# ggsave("analysis/figures/unmatched_vs_matched_events_on_tc_nomad.pdf", p, width = 10, height = 8)