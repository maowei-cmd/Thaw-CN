//
//  ChineseCatalogTests.swift
//  Project: Thaw
//
//  Copyright (Thaw) © 2026 Toni Förster
//  Licensed under the GNU GPLv3

import Foundation
import Testing

/// Checks the compiled zh-Hans table, so a broken catalog fails tests rather
/// than showing up as an English string in the app.
@Suite("Chinese catalog")
struct ChineseCatalogTests {
    private static func zhStrings() throws -> [String: String] {
        let path = try #require(Bundle.main.path(forResource: "zh-Hans", ofType: "lproj"))
        let url = URL(fileURLWithPath: path).appendingPathComponent("Localizable.strings")
        let data = try Data(contentsOf: url)
        let plist = try PropertyListSerialization.propertyList(from: data, options: [], format: nil)
        return try #require(plist as? [String: String])
    }

    @Test("The compiled catalog carries the full Chinese table")
    func catalogIsComplete() throws {
        let strings = try Self.zhStrings()
        #expect(strings.count >= 1870, "compiled zh-Hans has \(strings.count) entries")
        #expect(strings["Visible"] == "显示")
        #expect(strings["Hidden"] == "隐藏")
        #expect(strings["Always Hidden"] == "永久隐藏")
        #expect(strings["Close"] == "关闭")
        #expect(strings["About"] == "关于")
        #expect(strings["Cancel"] == "取消")
    }

    @Test("Every format specifier survives translation")
    func formatSpecifiersMatch() throws {
        let strings = try Self.zhStrings()
        let mismatches = strings.filter { key, value in
            Self.formats(in: key) != Self.formats(in: value)
        }.keys
        #expect(mismatches.isEmpty, "\(Array(mismatches.prefix(5)))")
    }

    /// Format specifiers without their positional index, so `%1$@ %2$@`
    /// matches `%@ %@` while `%lld` still has to match `%lld`.
    private static func formats(in string: String) -> [String] {
        guard let regex = try? NSRegularExpression(
            pattern: #"%(\d+\$)?([-+ #0']*)(\d+)?(?:\.(\d+))?(hh|h|ll|l|q|L|z|t|j)?([@diuUxXoOfFeEgGcCsSpaA%])"#
        ) else {
            return []
        }
        let text = string as NSString
        var result: [String] = []
        for match in regex.matches(in: string, range: NSRange(location: 0, length: text.length)) {
            let conversion = text.substring(with: match.range(at: 6))
            if conversion == "%" {
                continue
            }
            let flags = match.range(at: 2).location == NSNotFound ? "" : text.substring(with: match.range(at: 2))
            let width = match.range(at: 3).location == NSNotFound ? "" : text.substring(with: match.range(at: 3))
            let precision = match.range(at: 4).location == NSNotFound ? "" : "." + text.substring(with: match.range(at: 4))
            let length = match.range(at: 5).location == NSNotFound ? "" : text.substring(with: match.range(at: 5))
            result.append("%" + flags + width + precision + length + conversion)
        }
        return result.sorted()
    }
}
